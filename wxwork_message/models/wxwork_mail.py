# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import ast
import base64
import datetime
import logging
import psycopg2
import smtplib
import threading
import re

from collections import defaultdict

from odoo import _, api, fields, models
from odoo import tools
from odoo.addons.base.models.ir_mail_server import MailDeliveryException

_logger = logging.getLogger(__name__)


class WxWorkMail(models.Model):
    """ 
        保留要发送的企业微信消息模型。
        该模型提供排队和发送新消息的功能。
        参考模型 'mail.mail'
    """

    _name = "wxowrk.mail"
    _description = "Enterprise WeChat Outgoing message"
    _inherits = {"mail.message": "mail_message_id"}
    _order = "id desc"
    _rec_name = "subject"

    # 内容
    mail_message_id = fields.Many2one(
        "mail.message",
        "Message",
        required=True,
        ondelete="cascade",
        index=True,
        auto_join=True,
    )
    body_html = fields.Text("Rich-text Contents", help="Rich-text/HTML message")
    references = fields.Text(
        "References",
        help="Message references, such as identifiers of previous messages",
        readonly=1,
    )
    headers = fields.Text("Headers", copy=False)
    # 基于create() 自动检测 - 如果传递了'mail_message_id'，则此邮件为通知，在unlink() 期间，我们将不会级联删除父级及其附件
    notification = fields.Boolean(
        "Is Notification",
        help="Mail has been created to notify people of an existing mail.message",
    )
    # 收件人：包括不活跃的合作伙伴（他们可能已在发送消息后被存档，但在关系中仍应保持可见）
    email_to = fields.Text("To", help="Message recipients (emails)")
    email_cc = fields.Char("Cc", help="Carbon copy message recipients")
    recipient_ids = fields.Many2many(
        "res.partner", string="To (Partners)", context={"active_test": False}
    )
    # process
    state = fields.Selection(
        [
            ("outgoing", "Outgoing"),
            ("sent", "Sent"),
            ("received", "Received"),
            ("exception", "Delivery Failed"),
            ("cancel", "Cancelled"),
        ],
        "Status",
        readonly=True,
        copy=False,
        default="outgoing",
    )
    auto_delete = fields.Boolean(
        "Auto Delete",
        help="This option permanently removes any track of email after it's been sent, including from the Technical menu in the Settings, in order to preserve storage space of your Odoo database.",
    )
    failure_reason = fields.Text(
        "Failure Reason",
        readonly=1,
        help="Failure reason. This is usually the exception thrown by the email server, stored to ease the debugging of mailing issues.",
    )
    scheduled_date = fields.Char(
        "Scheduled Send Date",
        help="If set, the queue manager will send the email after the date. If not set, the email will be send as soon as possible.",
    )

    @api.model_create_multi
    def create(self, values_list):
        # notification field: if not set, set if mail comes from an existing mail.message
        # 通知字段：如果未设置，则设置邮件是否来自现有邮件。
        for values in values_list:
            if "notification" not in values and values.get("mail_message_id"):
                values["notification"] = True

        new_mails = super(WxWorkMail, self).create(values_list)

        new_mails_w_attach = self
        for mail, values in zip(new_mails, values_list):
            if values.get("attachment_ids"):
                new_mails_w_attach += mail
        if new_mails_w_attach:
            new_mails_w_attach.mapped("attachment_ids").check(mode="read")

        return new_mails

    def write(self, vals):
        res = super(WxWorkMail, self).write(vals)
        if vals.get("attachment_ids"):
            for mail in self:
                mail.attachment_ids.check(mode="read")
        return res

    def unlink(self):
        # cascade-delete the parent message for all mails that are not created for a notification
        # 级联删除未为通知创建的所有邮件的父邮件
        mail_msg_cascade_ids = [
            mail.mail_message_id.id for mail in self if not mail.notification
        ]
        res = super(WxWorkMail, self).unlink()
        if mail_msg_cascade_ids:
            self.env["mail.message"].browse(mail_msg_cascade_ids).unlink()
        return res

    @api.model
    def default_get(self, fields):
        # protection for `default_type` values leaking from menu action context (e.g. for invoices)
        # 保护从菜单操作上下文中泄漏的“ default_type”值（例如，针对发票）
        # To remove when automatic context propagation is removed in web client
        # 在Web客户端中删除自动上下文传播时删除
        if (
            self._context.get("default_type")
            not in type(self).message_type.base_field.selection
        ):
            self = self.with_context(dict(self._context, default_type=None))
        return super(WxWorkMail, self).default_get(fields)

    def mark_outgoing(self):
        return self.write({"state": "outgoing"})

    def cancel(self):
        return self.write({"state": "cancel"})

    @api.model
    def process_email_queue(self, ids=None):
        """
        立即发送排队的消息，并在每条消息发送后提交-这不是事务性的，不应在另一个事务中调用！ 

        :param list ids: 要发送的电子邮件ID的可选列表。 如果通过，则不执行搜索，而是使用这些ID。 
        :param dict context: 如果上下文中存在“过滤器”键，则此值将用作附加过滤器，以进一步限制要发送的传出消息（默认情况下，所有“传出”消息都已发送）。 
        """
        filters = [
            "&",
            ("state", "=", "outgoing"),
            "|",
            ("scheduled_date", "<", datetime.datetime.now()),
            ("scheduled_date", "=", False),
        ]
        if "filters" in self._context:
            filters.extend(self._context["filters"])
        # TODO: make limit configurable
        filtered_ids = self.search(filters, limit=10000).ids
        if not ids:
            ids = filtered_ids
        else:
            ids = list(set(filtered_ids) & set(ids))
        ids.sort()

        res = None
        try:
            # auto-commit except in testing mode
            auto_commit = not getattr(threading.currentThread(), "testing", False)
            res = self.browse(ids).send(auto_commit=auto_commit)
        except Exception:
            _logger.exception("Failed processing mail queue")
        return res

    def _postprocess_sent_message(
        self, success_pids, failure_reason=False, failure_type=None
    ):
        """
        成功发送邮件后，请执行所有必要的后处理，包括如果已设置邮件的auto_delete标志，则将其及其附件完全删除。 被子类覆盖，以实现额外的后处理行为。 

        :return: True
        """
        notif_mails_ids = [mail.id for mail in self if mail.notification]
        if notif_mails_ids:
            notifications = self.env["mail.notification"].search(
                [
                    ("notification_type", "=", "email"),
                    ("mail_id", "in", notif_mails_ids),
                    ("notification_status", "not in", ("sent", "canceled")),
                ]
            )
            if notifications:
                # find all notification linked to a failure
                # 查找所有链接到失败的通知
                failed = self.env["mail.notification"]
                if failure_type:
                    failed = notifications.filtered(
                        lambda notif: notif.res_partner_id not in success_pids
                    )
                (notifications - failed).sudo().write(
                    {
                        "notification_status": "sent",
                        "failure_type": "",
                        "failure_reason": "",
                    }
                )
                if failed:
                    failed.sudo().write(
                        {
                            "notification_status": "exception",
                            "failure_type": failure_type,
                            "failure_reason": failure_reason,
                        }
                    )
                    messages = notifications.mapped("mail_message_id").filtered(
                        lambda m: m.is_thread_message()
                    )
                    # TDE TODO: could be great to notify message-based, not notifications-based, to lessen number of notifs
                    messages._notify_message_notification_update()  # notify user that we have a failure
        if (
            not failure_type or failure_type == "RECIPIENT"
        ):  # if we have another error, we want to keep the mail.
            mail_to_delete_ids = [mail.id for mail in self if mail.auto_delete]
            self.browse(mail_to_delete_ids).sudo().unlink()
        return True

    # ------------------------------------------------------
    # mail_mail formatting, tools and send mechanism
    # mail_mail格式，工具和发送机制
    # ------------------------------------------------------

    def _send_prepare_body(self):
        """
        返回特定的ir_email正文。 继承此方法的主要目的是根据某些模块添加自定义内容。 
        """
        self.ensure_one()
        return self.body_html or ""

    def _send_prepare_values(self, partner=None):
        """Return a dictionary for specific email values, depending on a
        partner, or generic to the whole recipients given by mail.email_to.

            :param Model partner: specific recipient partner
        """
        self.ensure_one()
        body = self._send_prepare_body()
        body_alternative = tools.html2plaintext(body)
        if partner:
            email_to = [
                tools.formataddr((partner.name or "False", partner.email or "False"))
            ]
        else:
            email_to = tools.email_split_and_format(self.email_to)
        res = {
            "body": body,
            "body_alternative": body_alternative,
            "email_to": email_to,
        }
        return res

    def _split_by_server(self):
        """Returns an iterator of pairs `(mail_server_id, record_ids)` for current recordset.

        The same `mail_server_id` may repeat in order to limit batch size according to
        the `mail.session.batch.size` system parameter.
        """
        groups = defaultdict(list)
        # Turn prefetch OFF to avoid MemoryError on very large mail queues, we only care
        # about the mail server ids in this case.
        for mail in self.with_context(prefetch_fields=False):
            groups[mail.mail_server_id.id].append(mail.id)
        sys_params = self.env["ir.config_parameter"].sudo()
        batch_size = int(sys_params.get_param("mail.session.batch.size", 1000))
        for server_id, record_ids in groups.items():
            for mail_batch in tools.split_every(batch_size, record_ids):
                yield server_id, mail_batch

    def send(self, auto_commit=False, raise_exception=False):
        """ 
        立即发送选定的电子邮件，而忽略它们的当前状态（除非已被重新发送，否则不应传递已发送的电子邮件）。
        成功发送的电子邮件被标记为“已发送”，而失败发送的电子邮件被标记为“例外”，并且相应的错误邮件将输出到服务器日志中。 

        :param bool auto_commit:发送每封邮件后是否强制提交邮件状态（仅用于调度程序处理）；
                                在正常传递中，绝对不能为True（默认值：False）
        :param bool raise_exception: 如果电子邮件发送过程失败，是否引发异常 
        :return: True
        """
        for server_id, batch_ids in self._split_by_server():
            smtp_session = None
            try:
                smtp_session = self.env["ir.mail_server"].connect(
                    mail_server_id=server_id
                )
            except Exception as exc:
                if raise_exception:
                    # 为了与mail_mail.send（）引发的异常保持一致并向后兼容，将其封装到Odoo MailDeliveryException中
                    raise MailDeliveryException(
                        _("Unable to connect to SMTP Server"), exc
                    )
                else:
                    batch = self.browse(batch_ids)
                    batch.write({"state": "exception", "failure_reason": exc})
                    batch._postprocess_sent_message(
                        success_pids=[], failure_type="SMTP"
                    )
            else:
                self.browse(batch_ids)._send(
                    auto_commit=auto_commit,
                    raise_exception=raise_exception,
                    smtp_session=smtp_session,
                )
                _logger.info(
                    "Sent batch %s emails via mail server ID #%s",
                    len(batch_ids),
                    server_id,
                )
            finally:
                if smtp_session:
                    smtp_session.quit()

    def _send(self, auto_commit=False, raise_exception=False, smtp_session=None):
        IrMailServer = self.env["ir.mail_server"]
        IrAttachment = self.env["ir.attachment"]
        for mail_id in self.ids:
            success_pids = []
            failure_type = None
            processing_pid = None
            mail = None
            try:
                mail = self.browse(mail_id)
                if mail.state != "outgoing":
                    if mail.state != "exception" and mail.auto_delete:
                        mail.sudo().unlink()
                    continue

                # remove attachments if user send the link with the access_token
                body = mail.body_html or ""
                attachments = mail.attachment_ids
                for link in re.findall(r"/web/(?:content|image)/([0-9]+)", body):
                    attachments = attachments - IrAttachment.browse(int(link))

                # load attachment binary data with a separate read(), as prefetching all
                # `datas` (binary field) could bloat the browse cache, triggerring
                # soft/hard mem limits with temporary data.
                attachments = [
                    (a["name"], base64.b64decode(a["datas"]), a["mimetype"])
                    for a in attachments.sudo().read(["name", "datas", "mimetype"])
                    if a["datas"] is not False
                ]

                # specific behavior to customize the send email for notified partners
                email_list = []
                if mail.email_to:
                    email_list.append(mail._send_prepare_values())
                for partner in mail.recipient_ids:
                    values = mail._send_prepare_values(partner=partner)
                    values["partner_id"] = partner
                    email_list.append(values)

                # headers
                headers = {}
                ICP = self.env["ir.config_parameter"].sudo()
                bounce_alias = ICP.get_param("mail.bounce.alias")
                catchall_domain = ICP.get_param("mail.catchall.domain")
                if bounce_alias and catchall_domain:
                    if mail.mail_message_id.is_thread_message():
                        headers["Return-Path"] = "%s+%d-%s-%d@%s" % (
                            bounce_alias,
                            mail.id,
                            mail.model,
                            mail.res_id,
                            catchall_domain,
                        )
                    else:
                        headers["Return-Path"] = "%s+%d@%s" % (
                            bounce_alias,
                            mail.id,
                            catchall_domain,
                        )
                if mail.headers:
                    try:
                        headers.update(ast.literal_eval(mail.headers))
                    except Exception:
                        pass

                # Writing on the mail object may fail (e.g. lock on user) which
                # would trigger a rollback *after* actually sending the email.
                # To avoid sending twice the same email, provoke the failure earlier
                mail.write(
                    {
                        "state": "exception",
                        "failure_reason": _(
                            "Error without exception. Probably due do sending an email without computed recipients."
                        ),
                    }
                )
                # Update notification in a transient exception state to avoid concurrent
                # update in case an email bounces while sending all emails related to current
                # mail record.
                notifs = self.env["mail.notification"].search(
                    [
                        ("notification_type", "=", "email"),
                        ("mail_id", "in", mail.ids),
                        ("notification_status", "not in", ("sent", "canceled")),
                    ]
                )
                if notifs:
                    notif_msg = _(
                        "Error without exception. Probably due do concurrent access update of notification records. Please see with an administrator."
                    )
                    notifs.sudo().write(
                        {
                            "notification_status": "exception",
                            "failure_type": "UNKNOWN",
                            "failure_reason": notif_msg,
                        }
                    )
                    # `test_mail_bounce_during_send`, force immediate update to obtain the lock.
                    # see rev. 56596e5240ef920df14d99087451ce6f06ac6d36
                    notifs.flush(
                        fnames=[
                            "notification_status",
                            "failure_type",
                            "failure_reason",
                        ],
                        records=notifs,
                    )

                # build an RFC2822 email.message.Message object and send it without queuing
                res = None
                for email in email_list:
                    msg = IrMailServer.build_email(
                        email_from=mail.email_from,
                        email_to=email.get("email_to"),
                        subject=mail.subject,
                        body=email.get("body"),
                        body_alternative=email.get("body_alternative"),
                        email_cc=tools.email_split(mail.email_cc),
                        reply_to=mail.reply_to,
                        attachments=attachments,
                        message_id=mail.message_id,
                        references=mail.references,
                        object_id=mail.res_id and ("%s-%s" % (mail.res_id, mail.model)),
                        subtype="html",
                        subtype_alternative="plain",
                        headers=headers,
                    )
                    processing_pid = email.pop("partner_id", None)
                    try:
                        res = IrMailServer.send_email(
                            msg,
                            mail_server_id=mail.mail_server_id.id,
                            smtp_session=smtp_session,
                        )
                        if processing_pid:
                            success_pids.append(processing_pid)
                        processing_pid = None
                    except AssertionError as error:
                        if str(error) == IrMailServer.NO_VALID_RECIPIENT:
                            failure_type = "RECIPIENT"
                            # No valid recipient found for this particular
                            # mail item -> ignore error to avoid blocking
                            # delivery to next recipients, if any. If this is
                            # the only recipient, the mail will show as failed.
                            _logger.info(
                                "Ignoring invalid recipients for mail.mail %s: %s",
                                mail.message_id,
                                email.get("email_to"),
                            )
                        else:
                            raise
                if res:  # mail has been sent at least once, no major exception occured
                    mail.write(
                        {"state": "sent", "message_id": res, "failure_reason": False}
                    )
                    _logger.info(
                        "Mail with ID %r and Message-Id %r successfully sent",
                        mail.id,
                        mail.message_id,
                    )
                    # /!\ can't use mail.state here, as mail.refresh() will cause an error
                    # see revid:odo@openerp.com-20120622152536-42b2s28lvdv3odyr in 6.1
                mail._postprocess_sent_message(
                    success_pids=success_pids, failure_type=failure_type
                )
            except MemoryError:
                # prevent catching transient MemoryErrors, bubble up to notify user or abort cron job
                # instead of marking the mail as failed
                _logger.exception(
                    "MemoryError while processing mail with ID %r and Msg-Id %r. Consider raising the --limit-memory-hard startup option",
                    mail.id,
                    mail.message_id,
                )
                # mail status will stay on ongoing since transaction will be rollback
                raise
            except (psycopg2.Error, smtplib.SMTPServerDisconnected):
                # If an error with the database or SMTP session occurs, chances are that the cursor
                # or SMTP session are unusable, causing further errors when trying to save the state.
                _logger.exception(
                    "Exception while processing mail with ID %r and Msg-Id %r.",
                    mail.id,
                    mail.message_id,
                )
                raise
            except Exception as e:
                failure_reason = tools.ustr(e)
                _logger.exception(
                    "failed sending mail (id: %s) due to %s", mail.id, failure_reason
                )
                mail.write({"state": "exception", "failure_reason": failure_reason})
                mail._postprocess_sent_message(
                    success_pids=success_pids,
                    failure_reason=failure_reason,
                    failure_type="UNKNOWN",
                )
                if raise_exception:
                    if isinstance(e, (AssertionError, UnicodeEncodeError)):
                        if isinstance(e, UnicodeEncodeError):
                            value = "Invalid text: %s" % e.object
                        else:
                            value = ". ".join(e.args)
                        raise MailDeliveryException(value)
                    raise

            if auto_commit is True:
                self._cr.commit()
        return True

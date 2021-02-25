# -*- coding: utf-8 -*-

import datetime
import logging
import threading
from odoo import _, api, fields, models
from odoo import tools
from odoo.exceptions import UserError
from odoo.addons.wxwork_api.api.error_code import Errcode

_logger = logging.getLogger(__name__)


class MailMail(models.Model):
    _inherit = "mail.mail"

    msgtype = fields.Char(string="Message type",)
    media_id = fields.Char(string="Media file id",)
    message_to_all = fields.Boolean("To all members",)
    message_to_user = fields.Char(string="To User",)
    message_to_party = fields.Char(string="To Departments",)
    message_to_tag = fields.Char(string="To Tags",)
    body_text = fields.Text("Text Contents",)

    safe = fields.Selection(
        [
            ("0", "Shareable"),
            ("1", "Cannot share and content shows watermark"),
            ("2", "Only share within the company "),
        ],
        string="Secret message",
        required=True,
        default="1",
        readonly=True,
        help="表示是否是保密消息，0表示可对外分享，1表示不能分享且内容显示水印，2表示仅限在企业内分享，默认为0；注意仅mpnews类型的消息支持safe值为2，其他消息类型不支持",
    )

    enable_id_trans = fields.Boolean(
        string="Turn on id translation", help="表示是否开启id转译，0表示否，1表示是，默认0", default=False
    )
    enable_duplicate_check = fields.Boolean(
        string="Turn on duplicate message checking",
        help="表示是否开启重复消息检查，0表示否，1表示是，默认0",
        default=False,
    )
    duplicate_check_interval = fields.Integer(
        string="Time interval for repeated message checking",
        help="表示是否重复消息检查的时间间隔，默认1800s，最大不超过4小时",
        default="1800",
    )

    @api.model
    def process_email_queue(self, ids=None):
        """
        立即发送排队的消息，在每条消息发送后提交-这不是事务性的，不应在另一个事务中调用！ 

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
            # 自动提交（测试模式除外）
            auto_commit = not getattr(threading.currentThread(), "testing", False)
            if self.notification_type == "wxwork":
                res = self.browse(ids).send_wxwork_message(auto_commit=auto_commit)
            else:
                res = self.browse(ids).send(auto_commit=auto_commit)
        except Exception:
            _logger.exception(_("Failed processing mail queue"))
        return res

    def _postprocess_sent_wxwork_message(
        self, success_pids, failure_reason=False, failure_type=None
    ):
        """
        成功发送``mail``后，请执行所有必要的后处理，包括如果已设置邮件的auto_delete标志，则将其及其附件完全删除。
        被子类覆盖，以实现额外的后处理行为。 

        :return: True
        """
        notif_mails_ids = [mail.id for mail in self if mail.notification]
        if notif_mails_ids:
            notifications = self.env["mail.notification"].search(
                [
                    ("notification_type", "=", "wxwork"),
                    ("mail_id", "in", notif_mails_ids),
                    ("notification_status", "not in", ("sent", "canceled")),
                ]
            )
            if notifications:
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
                    # TDE TODO: 通知基于消息而不是基于通知的通知，以减少通知数量可能会很棒
                    messages._notify_message_notification_update()  # 通知用户我们失败了
            if not failure_type or failure_type == "RECIPIENT":  # 如果还有另一个错误，我们要保留邮件。
                mail_to_delete_ids = [mail.id for mail in self if mail.auto_delete]
                self.browse(mail_to_delete_ids).sudo().unlink()

        return True

    # ------------------------------------------------------
    # 消息格式、工具和发送机制
    # ------------------------------------------------------
    def _send_message_prepare_body(self):
        """
        返回特定的ir_email正文。 继承此方法的主要目的是根据某些模块添加自定义内容。 
        """
        self.ensure_one()
        return self.body_html or ""

    def _send_message_prepare_values(self, partner=None):
        """
        根据合作伙伴返回特定电子邮件值的字典，或者返回由mail.message_to_user mail.message_to_party  mail.message_to_tag 给出的整个收件人通用的字典。
        :param Model partner: 具体的收件人合作伙伴 
        """
        self.ensure_one()
        body = self._send_message_prepare_body()
        body_alternative = tools.html2plaintext(body)
        if partner:
            message_to_user = [
                tools.formataddr(
                    (partner.name or "False", partner.wxwork_id or "False")
                )
            ]
        else:
            message_to_user = tools.email_split_and_format(self.email_to)
        res = {
            "body": body,
            "body_alternative": body_alternative,
            "message_to_user": message_to_user,
        }
        return res

    def _send_wxwork_prepare_values(self, partner=None):
        """
        根据合作伙伴返回有关特定电子邮件值的字典，或者对整个邮件都是通用的。对于特定电子邮件值取决于对伙伴的字典，或者对mail.email_to给出的整个收件人来说都是通用的。 

        :param Model partner: 具体的收件人合作伙伴 
        """
        self.ensure_one()
        body_html = self._send_prepare_body()
        # body_alternative = tools.html2plaintext(body_html)
        if partner:
            email_to = [
                tools.formataddr((partner.name or "False", partner.email or "False"))
            ]
            message_to_user = [
                tools.formataddr(
                    (partner.name or "False", partner.message_to_user or "False")
                )
            ]
        else:
            email_to = tools.email_split_and_format(self.email_to)
            message_to_user = tools.email_split_and_format(self.message_to_user)
        res = {
            # "subject": subject,
            "body_html": body_html,
            # "message_to_user": message_to_user,
        }

        return res

    def send_wxwork_message(self, auto_commit=False, raise_exception=False):
        """
        立即发送选定的电子邮件，而忽略它们的当前状态（除非已被重新发送，否则不应传递已发送的电子邮件）。
成功发送的电子邮件被标记为“已发送”，而失败发送的电子邮件被标记为“例外”，并且相应的错误邮件将输出到服务器日志中。
        :param bool auto_commit：发送每封邮件后是否强制提交邮件状态（仅用于调度程序处理）；
                 在正常发送绝对不能为True（默认值：False） 
        :param bool raise_exception：如果电子邮件发送过程失败，是否引发异常 
        :return: True
        """

        sys_params = self.env["ir.config_parameter"].sudo()
        corpid = sys_params.get_param("wxwork.corpid")
        secret = sys_params.get_param("wxwork.message_secret")
        message_agentid = sys_params.get_param("wxwork.message_agentid")

        if "xxxxxxxxxxxxxxxxxx" in corpid or corpid is None or corpid is False:
            raise UserError(_("Please fill in the company ID"))
        elif (
            "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" in secret
            or secret is None
            or secret is False
        ):
            raise UserError(
                _("Please fill in the application secret of the message push")
            )
        elif (
            "0000000" in message_agentid
            or message_agentid is None
            or message_agentid is False
        ):
            raise UserError(_("Please fill in the application ID of the message push"))
        else:
            for batch_ids in self._split_by_server():
                # TODO 待处理多公司-企业微信互联功能

                self.browse(batch_ids)._send_wxwork_message(
                    auto_commit=auto_commit, raise_exception=raise_exception,
                )
                _logger.info(
                    _("Sent batch %s messages"), len(batch_ids),
                )

    def _send_wxwork_message(
        self, auto_commit=False, raise_exception=False,
    ):
        IrWxWorkMessageApi = self.env["wxwork.message.api"]
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
                # 为通知的合作伙伴自定义发送电子邮件的特定行为
                email_list = []
                if mail.message_to_user or mail.message_to_party or mail.message_to_tag:
                    email_list.append(mail._send_message_prepare_values())
                for partner in mail.recipient_ids:
                    values = mail._send_message_prepare_values(partner=partner)
                    values["partner_id"] = partner
                    email_list.append(values)

                # 在邮件对象上写入可能会失败（例如锁定用户），这将在*实际发送电子邮件后触发回滚。
                # 为了避免两次发送同一封电子邮件，请尽早引发失败
                mail.write(
                    {
                        "state": "exception",
                        "failure_reason": _(
                            "Error without exception. Probably due do sending an email without computed recipients."
                        ),
                    }
                )
                # 在临时异常状态下更新通知，以避免在发送与当前邮件记录相关的所有电子邮件时发生电子邮件反弹的情况下进行并发更新。
                notifs = self.env["mail.notification"].search(
                    [
                        ("notification_type", "=", "wxwork"),
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
                    # `test_mail_bounce_during_send`，强制立即更新以获取锁定。
                    # 见修订版。56596e5240ef920df14d99087451ce6f06ac6d36
                    notifs.flush(
                        fnames=[
                            "notification_status",
                            "failure_type",
                            "failure_reason",
                        ],
                        records=notifs,
                    )
                # 建立电子邮件.message.message对象并在不排队的情况下发送它
                res = None
                for email in email_list:
                    msg = IrWxWorkMessageApi.build_message(
                        msgtype=mail.msgtype,
                        toall=mail.message_to_all,
                        touser=mail.message_to_user,
                        toparty=mail.message_to_party,
                        totag=mail.message_to_tag,
                        subject=mail.subject,
                        media_id=mail.media_id,
                        description=mail.description,
                        author_id=mail.author_id,
                        body_html=mail.body_html,
                        body_text=mail.body_text,
                        safe=mail.safe,
                        enable_id_trans=mail.enable_id_trans,
                        enable_duplicate_check=mail.enable_duplicate_check,
                        duplicate_check_interval=mail.duplicate_check_interval,
                    )
                    processing_pid = email.pop("partner_id", None)
                    try:
                        res = IrWxWorkMessageApi.send_by_api(msg)
                        if processing_pid:
                            success_pids.append(processing_pid)
                        processing_pid = None
                    except AssertionError as error:
                        pass

                if res:  # 消息已至少发送一次，未发生重大异常
                    if "errcode" in res:
                        if res.get("errcode") == 0:
                            failure_reason = ""
                            # 处理无效的接收人
                            if "invaliduser" in res:
                                if res.get("invaliduser") != "":
                                    failure_reason += _(
                                        "Unable to send to invalid user: %s\n"
                                    ) % res.get("invaliduser")
                            if "invalidparty" in res:
                                if res.get("invalidparty") != "":
                                    failure_reason += _(
                                        "Unable to send to invalid department: %s\n"
                                    ) % res.get("invalidparty")
                            if "invalidtag" in res:
                                if res.get("invalidtag") != "":
                                    failure_reason += _(
                                        "Unable to send to invalid tag: %s"
                                    ) % res.get("invalidtag")
                            mail.write(
                                {
                                    "state": "sent",
                                    "message_id": res,
                                    "failure_reason": failure_reason,
                                }
                            )

                            _logger.info(
                                _(
                                    "Message with ID %r and Message-Id %r successfully sent",
                                    mail.id,
                                    mail.message_id,
                                )
                            )
                        else:
                            failure_reason = _(
                                "Error code: %s,\nError description: %s,\nError Details: %s"
                            ) % (
                                str(res.get("errcode")),
                                Errcode.getErrcode(res.get("errcode")),
                                res.get("errmsg"),
                            )
                            _logger.exception(
                                _("failed sending message (id: %s) due to %s")
                                % (mail.id, failure_reason,)
                            )
                            mail.write(
                                {
                                    "state": "exception",
                                    "failure_reason": failure_reason,
                                }
                            )
                else:
                    failure_reason = _("Unknown reason")
                    _logger.exception(
                        _("failed sending message (id: %s) due to %s")
                        % (mail.id, failure_reason,)
                    )
                    mail.write(
                        {"state": "exception", "failure_reason": failure_reason,}
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

            if auto_commit is True:
                self._cr.commit()
        return True


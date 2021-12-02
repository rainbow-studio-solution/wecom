# -*- coding: utf-8 -*-

import logging
import ast
import base64
import datetime
import logging
import psycopg2
import smtplib
import re
from odoo import _, api, fields, models
from odoo import tools
from odoo.addons.base.models.ir_mail_server import MailDeliveryException
from odoo.exceptions import UserError, Warning
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException

_logger = logging.getLogger(__name__)


class MailMail(models.Model):
    _inherit = "mail.mail"

    is_wecom_message = fields.Boolean("Is WeCom Message")
    msgtype = fields.Char(
        string="Message type",
    )
    media_id = fields.Char(
        string="Media file id",
    )

    message_to_user = fields.Char(
        string="To User",
    )
    message_to_party = fields.Char(
        string="To Departments",
    )
    message_to_tag = fields.Char(
        string="To Tags",
    )
    body_json = fields.Text(
        "Json Contents",
    )

    body_markdown = fields.Text(
        "Markdown Contents",
    )

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
        help="Indicates whether it is a confidential message, 0 indicates that it can be shared externally, 1 indicates that it cannot be shared and the content displays watermark, 2 indicates that it can only be shared within the enterprise, and the default is 0; Note that only messages of mpnews type support the safe value of 2, and other message types do not",
    )

    enable_id_trans = fields.Boolean(
        string="Turn on id translation",
        help="Indicates whether to enable ID translation, 0 indicates no, 1 indicates yes, and 0 is the default",
        default=False,
    )
    enable_duplicate_check = fields.Boolean(
        string="Turn on duplicate message checking",
        help="Indicates whether to enable duplicate message checking. 0 indicates no, 1 indicates yes. The default is 0",
        default=False,
    )
    duplicate_check_interval = fields.Integer(
        string="Time interval for repeated message checking",
        help="Indicates whether the message check is repeated. The default is 1800s and the maximum is no more than 4 hours",
        default="1800",
    )

    def _postprocess_sent_wecom_message(
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
                    ("notification_type", "=", "email"),
                    ("is_wecom_message", "=", True),
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
                        "is_wecom_message": True,
                        "failure_type": "",
                        "failure_reason": "",
                    }
                )
                if failed:
                    failed.sudo().write(
                        {
                            "notification_status": "exception",
                            "is_wecom_message": True,
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
    # mail_mail formatting, tools and send mechanism
    # ------------------------------------------------------
    def _send_prepare_body_html(self):
        self.ensure_one()
        return self.body_html or ""

    def _send_prepare_body_json(self):
        self.ensure_one()
        return self.body_json or ""

    def _send_prepare_body_markdown(self):
        self.ensure_one()
        return self.body_markdown or ""

    def send(
        self,
        auto_commit=False,
        raise_exception=False,
        company=None,
    ):
        """
        立即发送选定的电子邮件，而忽略它们的当前状态（除非已被重新发送，否则不应该传递已经发送的电子邮件）。
        成功发送的电子邮件被标记为“已发送”，未发送成功的电子邮件被标记为“例外”，并且相应的错误邮件将输出到服务器日志中。

        :param bool auto_commit: 在发送每封邮件后是否强制提交邮件状态（仅用于调度程序处理）；
            在正常传递中，永远不应该为True（默认值：False）
        :param bool raise_exception: 如果电子邮件发送过程失败，将引发异常
        :param bool is_wecom_message: 标识是企业微信消息
        :param company: 公司
        :return: True
        """
        if not company:
            company = self.env.company
        for server_id, batch_ids in self._split_by_server():
            smtp_session = None
            try:
                if self.is_wecom_message:
                    # 标识为企业微信消息的 mail_mail 对象 pass掉
                    # print("mail.mail-send()-1")
                    pass
                else:
                    smtp_session = self.env["ir.mail_server"].connect(
                        mail_server_id=server_id
                    )
            except Exception as exc:
                if self.is_wecom_message:
                    # 标识为企业微信消息的 mail_mail 对象 pass掉
                    print("mail.mail-send()-2")
                    pass

                else:
                    if raise_exception:
                        # 为了与 mail_mail.send() 引发的异常保持一致并向后兼容，它被封装到一个Odoo MailDeliveryException中
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

                if self.is_wecom_message:
                    self.browse(batch_ids)._send_wecom_message(
                        auto_commit=auto_commit,
                        raise_exception=raise_exception,
                        company=company,
                    )
                    _logger.info("Sent batch %s messages via Wecom", len(batch_ids))
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
                if self.is_wecom_message:
                    # 标识为企业微信消息的 mail_mail 对象 pass掉
                    pass
                else:
                    if smtp_session:
                        smtp_session.quit()

    def _send_wecom_prepare_values(self, partner=None):
        """
        根据合作伙伴返回有关特定电子邮件值的字典，或者对整个邮件都是通用的。对于特定电子邮件值取决于对伙伴的字典，或者对mail.email_to给出的整个收件人来说都是通用的。

        :param Model partner: 具体的收件人合作伙伴
        """
        self.ensure_one()
        body_html = self._send_prepare_body_html()
        body_json = self._send_prepare_body_json()
        body_markdown = self._send_prepare_body_markdown()
        # body_alternative = tools.html2plaintext(body_html)
        if partner:
            email_to = [
                tools.formataddr((partner.name or "False", partner.email or "False"))
            ]
            message_to_user = [
                tools.formataddr(
                    (partner.name or "False", partner.wecom_userid or "False")
                )
            ]
        else:
            email_to = tools.email_split_and_format(self.email_to)
            message_to_user = self.message_to_user
        res = {
            # "message_body_text": message_body_text,
            # "message_body_html": message_body_html,
            "email_to": email_to,
            "message_to_user": message_to_user,
            "body_json": body_json,
            "body_html": body_html,
            "body_markdown": body_markdown,
        }

        return res

    def send_wecom_message(self, auto_commit=False, raise_exception=False):
        """ """

    def _send_wecom_message(
        self,
        auto_commit=False,
        raise_exception=False,
        company=None,
    ):
        """
        :param bool auto_commit: 发送每封邮件后是否强制提交邮件状态（仅用于调度程序处理）；
                 在正常发送绝对不能为True（默认值：False）
        :param bool raise_exception: 如果电子邮件发送过程失败，是否引发异常
        :return: True
        """
        if not company:
            company = self.env.company

        IrWxWorkMessageApi = self.env["wecom.message.api"]
        IrAttachment = self.env["ir.attachment"]
        for mail_id in self.ids:
            success_pids = []
            failure_type = None
            processing_pid = None
            mail = None
            mail = self.browse(mail_id)
            mail.mail_message_id.is_wecom_message = True  # 标识为企业微信消息
            mail.mail_message_id.is_internal = True  # 标识为企业微信消息

            if mail.state != "outgoing":
                if mail.state != "exception" and mail.auto_delete:
                    mail.sudo().unlink()
                continue

            # 如果用户发送带有访问令牌的链接，请删除附件
            body_html = mail.body_html or ""
            body_json = mail.body_json or ""
            body_markdown = mail.body_markdown or ""
            attachments = mail.attachment_ids
            for link in re.findall(r"/web/(?:content|image)/([0-9]+)", body_html):
                attachments = attachments - IrAttachment.browse(int(link))
            for link in re.findall(r"/web/(?:content|image)/([0-9]+)", body_json):
                attachments = attachments - IrAttachment.browse(int(link))
            for link in re.findall(r"/web/(?:content|image)/([0-9]+)", body_markdown):
                attachments = attachments - IrAttachment.browse(int(link))

            # 为通知的合作伙伴自定义发送电子邮件的特定行为
            email_list = []
            if mail.message_to_user or mail.message_to_party or mail.message_to_tag:
                email_list.append(mail._send_wecom_prepare_values())
            for partner in mail.recipient_ids:
                values = mail._send_wecom_prepare_values(partner=partner)
                values["partner_id"] = partner
                email_list.append(values)

            # 在邮件对象上写入可能会失败（例如锁定用户），这将在*实际发送电子邮件后触发回滚。
            # 为了避免两次发送同一封电子邮件，请尽早引发失败

            mail.write(
                {"is_wecom_message": True, "state": "sent", "failure_reason": ""}
            )

            # 在临时异常状态下更新通知，以避免在发送与当前邮件记录相关的所有电子邮件时发生电子邮件反弹的情况下进行并发更新。
            notifs = self.env["mail.notification"].search(
                [
                    ("notification_type", "=", "email"),
                    ("is_wecom_message", "=", True),
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
                    fnames=["notification_status", "failure_type", "failure_reason"],
                    records=notifs,
                )
                notifs.flush(
                    fnames=[
                        "notification_status",
                        "failure_type",
                        "failure_reason",
                    ],
                    records=notifs,
                )

                # 建立 email.message.message对象并在不排队的情况下发送它
                res = None
            for email in email_list:
                # print("----------1", email.get("body_json"))
                # print("----------2", mail.body_json)
                msg = IrWxWorkMessageApi.build_message(
                    msgtype=mail.msgtype,
                    touser=mail.message_to_user,
                    toparty=mail.message_to_party,
                    totag=mail.message_to_tag,
                    subject=mail.subject,
                    media_id=mail.media_id,
                    description=mail.description,
                    author_id=mail.author_id,
                    body_html=mail.body_html,
                    body_json=mail.body_json,
                    body_markdown=mail.body_markdown,
                    # body_html=email.get("body_html"),
                    # body_json=email.get("body_json"),
                    # body_markdown=email.get("body_markdown"),
                    safe=mail.safe,
                    enable_id_trans=mail.enable_id_trans,
                    enable_duplicate_check=mail.enable_duplicate_check,
                    duplicate_check_interval=mail.duplicate_check_interval,
                    company=company,
                )
                processing_pid = email.pop("partner_id", None)
                try:
                    # 通过API发送消息
                    res = IrWxWorkMessageApi.send_by_api(msg)
                    if processing_pid:
                        success_pids.append(processing_pid)
                    processing_pid = None
                except AssertionError as exc:
                    error = self.env["wecom.service_api_error"].get_error_by_code(
                        exc.errCode
                    )
                    mail.write(
                        {
                            "is_wecom_message": True,
                            "state": "exception",
                            "failure_reason": "%s %s"
                            % (str(error["code"]), error["name"]),
                        }
                    )
                    if raise_exception:
                        return self.env["wecomapi.tools.action"].ApiExceptionDialog(
                            exc, raise_exception
                        )

            if res["errcode"] == 0:  # 消息发送成功
                mail.write(
                    {
                        "is_wecom_message": True,
                        "state": "sent",
                        "message_id": res["msgid"],
                        "failure_reason": False,
                    }
                )
                _logger.info(
                    "Message with ID %r and Message-Id %r successfully sent",
                    mail.id,
                    mail.message_id,
                )

            if auto_commit is True:
                self._cr.commit()
        return True

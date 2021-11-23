# -*- coding: utf-8 -*-

import datetime
import logging
import threading
from odoo import _, api, fields, models
from odoo import tools
from odoo.addons.base.models.ir_mail_server import MailDeliveryException
from odoo.exceptions import UserError, Warning


_logger = logging.getLogger(__name__)


class MailMail(models.Model):
    _inherit = "mail.mail"

    is_wecom_message = fields.Boolean("WeCom Message")
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
    body_html = fields.Text(
        "Html Contents",
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
    def send_wecom_message(
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
        print("mail", company)
        if not company:
            company = self.env.company

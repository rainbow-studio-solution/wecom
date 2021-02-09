# -*- coding: utf-8 -*-

from collections import defaultdict
from operator import itemgetter

from odoo import exceptions, fields, models
from odoo.tools import groupby


class MailMessage(models.Model):
    """ 
    重写MailMessage类以添加新类型：企业微信消息。
    这些消息使用企业微信带有自己的通知方法
    """

    _inherit = "mail.message"

    message_type = fields.Selection(
        selection_add=[("wxwork", "Enterprise WeChat Message")],
        ondelete={"wxwork": lambda recs: recs.write({"message_type": "email"})},
    )

    has_wxwork_message_error = fields.Boolean(
        "Has Enterprise WeChat Message error",
        compute="_compute_has_wxwork_message_error",
        search="_search_has_wxwork_message_error",
        help="Has error",
    )

    def _compute_has_wxwork_message_error(self):
        sms_error_from_notification = (
            self.env["mail.notification"]
            .sudo()
            .search(
                [
                    ("notification_type", "=", "wxwork"),
                    ("mail_message_id", "in", self.ids),
                    ("notification_status", "=", "exception"),
                ]
            )
            .mapped("mail_message_id")
        )
        for message in self:
            message.has_wxwork_message_error = message in sms_error_from_notification

    def _search_has_wxwork_message_error(self, operator, operand):
        if operator == "=" and operand:
            return [
                "&",
                ("notification_ids.notification_status", "=", "exception"),
                ("notification_ids.notification_type", "=", "wxwork"),
            ]
        raise NotImplementedError()

    def message_format(self):
        """ 
        为了检索有关企业微信消息的数据而进行覆盖（收件人名称和企业微信消息状态） 

        TDE FIXME: clean the overall message_format thingy
        """
        message_values = super(MailMessage, self).message_format()
        all_sms_notifications = (
            self.env["mail.notification"]
            .sudo()
            .search(
                [
                    ("mail_message_id", "in", [r["id"] for r in message_values]),
                    ("notification_type", "=", "wxwork"),
                ]
            )
        )
        msgid_to_notif = defaultdict(lambda: self.env["mail.notification"].sudo())
        for notif in all_sms_notifications:
            msgid_to_notif[notif.mail_message_id.id] += notif

        for message in message_values:
            customer_sms_data = [
                (
                    notif.id,
                    notif.res_partner_id.display_name or notif.sms_number,
                    notif.notification_status,
                )
                for notif in msgid_to_notif.get(message["id"], [])
            ]
            message["wxwork_message_ids"] = customer_sms_data
        return message_values

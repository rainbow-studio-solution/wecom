# -*- coding: utf-8 -*-

from odoo import fields, models


class MailNotification(models.Model):
    _inherit = "mail.notification"

    is_wecom_message = fields.Boolean("WeCom Message")

    notification_status = fields.Selection(
        selection_add=[
            ("wecom_exception", "Send exception"),
            ("wecom_recall", "Recall"),
        ]
    )
    wecom_msgid = fields.Char("WeCom Message ID")

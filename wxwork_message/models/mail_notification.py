# -*- coding: utf-8 -*-

from odoo import fields, models


class MailNotification(models.Model):
    _inherit = "mail.notification"

    notification_type = fields.Selection(
        selection_add=[("wxwork", "Enterprise WeChat Message")],
        ondelete={"wxwork": "set default"},
    )
    sms_id = fields.Many2one(
        "wxwork.message",
        string="Enterprise WeChat Message",
        index=True,
        ondelete="set null",
    )
    # TODO sms_number
    sms_number = fields.Char("SMS Number")
    failure_type = fields.Selection(
        selection_add=[
            ("invalid_user", "Invalid User"),
            ("invalid_party", "Invalid Department"),
            ("invalid_tag", "Invalid Tag"),
        ]
    )

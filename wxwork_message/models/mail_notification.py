# -*- coding: utf-8 -*-

from odoo import fields, models


class MailNotification(models.Model):
    _inherit = "mail.notification"

    notification_type = fields.Selection(
        selection_add=[("wxwork", "Enterprise WeChat Message")],
        ondelete={"wxwork": "set default"},
    )
    message_id = fields.Many2one(
        "wxwork.message",
        string="Enterprise WeChat Message",
        index=True,
        ondelete="set null",
    )

    message_to_user = fields.Char(string="To Employees",)
    message_to_party = fields.Char(string="To Departments",)
    message_to_tag = fields.Char(string="To Tags",)
    failure_type = fields.Selection(
        selection_add=[
            ("invalid_user", "Invalid User"),
            ("invalid_party", "Invalid Department"),
            ("invalid_tag", "Invalid Tag"),
        ]
    )

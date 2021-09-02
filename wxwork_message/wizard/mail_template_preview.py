# -*- coding: utf-8 -*-

from odoo import api, fields, models


class MailTemplatePreview(models.TransientModel):
    _inherit = ["mail.template.preview"]
    # _name = "wxwork.message.template.preview"
    # _description = "Enterprise WeChat message Template Preview"

    _MAIL_TEMPLATE_FIELDS = [
        "subject",
        "body_html",
        "email_from",
        "email_to",
        "email_cc",
        "reply_to",
        "msgtype",
        "message_to_all",
        "message_to_user",
        "message_to_party",
        "message_to_tag",
        "message_body_json",
        "message_body_html",
        "scheduled_date",
        "attachment_ids",
    ]

    msgtype = fields.Char(
        string="Message type", compute="_compute_mail_template_fields"
    )
    message_to_all = fields.Boolean("To all members",)
    message_to_user = fields.Char(string="To Users", help="Message recipients (users)",)
    message_to_party = fields.Char(
        string="To Departments", help="Message recipients (departments)",
    )
    message_to_tag = fields.Char(string="To Tags", help="Message recipients (tags)",)
    message_body_json = fields.Text(
        "Text Body", compute="_compute_mail_template_fields"
    )
    message_body_html = fields.Html(
        "Html Body", compute="_compute_mail_template_fields"
    )


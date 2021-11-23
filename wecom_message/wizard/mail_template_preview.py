# -*- coding: utf-8 -*-

from odoo import api, fields, models


class MailTemplatePreview(models.TransientModel):
    _inherit = ["mail.template.preview"]
    # _name = "wecom.message.template.preview"
    # _description = "WeCom message Template Preview"

    _MAIL_TEMPLATE_FIELDS = [
        "subject",
        "body_html",
        "email_from",
        "email_to",
        "email_cc",
        "reply_to",
        "msgtype",
        "message_to_user",
        "message_to_party",
        "message_to_tag",
        "body_json",
        "body_html",
        "body_markdown",
        "scheduled_date",
        "attachment_ids",
    ]

    msgtype = fields.Char(
        string="Message type", compute="_compute_mail_template_fields"
    )

    message_to_user = fields.Char(
        string="To Users",
        help="Message recipients (users)",
    )
    message_to_party = fields.Char(
        string="To Departments",
        help="Message recipients (departments)",
    )
    message_to_tag = fields.Char(
        string="To Tags",
        help="Message recipients (tags)",
    )
    body_json = fields.Text("Json Body", compute="_compute_mail_template_fields")
    body_html = fields.Html("Html Body", compute="_compute_mail_template_fields")
    body_markdown = fields.Text(
        "Markdown Body", compute="_compute_mail_template_fields"
    )

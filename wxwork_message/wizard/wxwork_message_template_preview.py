# -*- coding: utf-8 -*-

from odoo import api, fields, models


class WxWorkMessageTemplatePreview(models.TransientModel):
    _inherit = ["mail.template.preview"]
    # _name = "wxwork.message.template.preview"
    # _description = "Enterprise WeChat message Template Preview"

    msgtype = fields.Char(
        string="Message type", compute="_compute_wxwork_message_template_msgtype_fields"
    )
    message_body_text = fields.Text(
        "Body", compute="_compute_wxwork_message_template_text_fields"
    )
    message_body_html = fields.Html(
        "Body", compute="_compute_wxwork_message_template_html_fields"
    )


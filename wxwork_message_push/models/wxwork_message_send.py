# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class MassMailing(models.Model):
    _name = "wxwoke.message.sending"
    _description = "Enterprise WeChat message sending"

    subject = fields.Char(
        "Subject", help="Subject of your Mailing", required=True, translate=True
    )

    to_user = fields.Text("To Users", help="Message recipients (users)")
    to_party = fields.Text("To Departments", help="Message recipients (departments)")
    to_tag = fields.Text("To Tags", help="Message recipients (tags)")

    use_templates = fields.Boolean("Use templates", translate=True)
    msgtype = fields.Selection(
        [
            ("text", "Text message"),
            ("image", "Picture message"),
            ("voice", "Voice messages"),
            ("video", "Video message"),
            ("file", "File message"),
            ("textcard", "Text card message"),
            ("news", "Graphic message"),
            ("mpnews", "Graphic message（mpnews）"),
            ("markdown", "Markdown message"),
            ("miniprogram", "Mini Program Notification Message"),
            ("taskcard", "Task card message"),
        ],
        string="Message type",
        required=True,
        default="markdown",
    )

    text = fields.Text("Text message content")
    image = fields.Text("Picture message content")
    video = fields.Text("Video message content")
    file = fields.Text("File message content")
    textcard = fields.Text("Text card message content")
    news = fields.Text("Graphic message content")
    mpnews = fields.Text("Graphic message (mpnews) content")
    markdown = fields.Text("Markdown message content")
    miniprogram_notice = fields.Text("Mini Program Notification Message")
    taskcard = fields.Text("Task card message content")


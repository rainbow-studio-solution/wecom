# -*- coding: utf-8 -*-

import base64
import logging


from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError
import html2text

_logger = logging.getLogger(__name__)


class MailTemplate(models.Model):
    _inherit = "mail.template"

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
        help="Policy on how to handle Chatter notifications:\n"
        "- Handle by Emails: notifications are sent to your email address\n"
        "- Handle in Odoo: notifications appear in your Odoo Inbox",
    )
    safe = fields.Boolean(string="Confidential message", default=False)
    wxwork_body_html = fields.Html(
        "Enterprise WeChat Message Body", translate=True, sanitize=False
    )
    enable_id_trans = fields.Boolean(
        string="Turn on id translation", help="表示是否开启id转译，0表示否，1表示是，默认0", default=False
    )
    enable_duplicate_check = fields.Boolean(
        string="Turn on duplicate message checking",
        help="表示是否开启重复消息检查，0表示否，1表示是，默认0",
        default=False,
    )
    duplicate_check_interval = fields.Integer(
        string="Time interval for repeated message checking",
        help="表示是否重复消息检查的时间间隔，默认1800s，最大不超过4小时",
        default="1800",
    )

    @api.model
    def copy_body_html(self):
        for template in self:
            if not template.wxwork_body_html:
                # 判断企业微信消息模板为空
                template.wxwork_body_html = self.html2text_handle(template.body_html)

    def html2text_handle(self, html):
        # 转换markdown格式
        if bool(html):
            return html2text.html2text(html)
        else:
            pass

    def send_mail(
        self,
        res_id,
        force_send=False,
        raise_exception=False,
        email_values=None,
        notif_layout=False,
    ):
        values = self.generate_email(
            res_id,
            [
                "subject",
                "body_html",
                "email_from",
                "email_to",
                "partner_to",
                "email_cc",
                "reply_to",
                "scheduled_date",
            ],
        )
        # res_id 是用户id
        if self.env["res.users"].browse(res_id).notification_type == "wxwork":
            # 拦截 用户通知类型为企业微信的发送方式
            values = self.env["wxwork.message.template"].generate_message(
                res_id,
                [
                    "subject",
                    "body_html",
                    "email_from",
                    "email_to",
                    "partner_to",
                    "email_cc",
                    "reply_to",
                    "scheduled_date",
                ],
            )
            print(values)

        return super(MailTemplate, self).send_mail(
            res_id,
            force_send=False,
            raise_exception=False,
            email_values=None,
            notif_layout=False,
        )

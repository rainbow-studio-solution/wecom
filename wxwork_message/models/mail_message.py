# -*- coding: utf-8 -*-

import logging
import threading

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class Message(models.Model):
    """ 
    系统通知（替换res.log通知），
评论（OpenChatter讨论）和收到的电子邮件。 
    """

    _inherit = "mail.message"
    # _name = "wxwork.message"
    # _description = "Outgoing Enterprise WeChat Message"
    # _rec_name = "number"
    # _order = "id DESC"

    API_TO_MESSAGE_STATE = {
        "success": "sent",
        "invaliduser": "Invalid user",
        "invalidparty": "Invalid party",
        "invalidtag": "Invalid tag",
        "api_error": "Api error",
    }

    message_type = fields.Selection(
        selection_add=[("wxwork", "Enterprise WeChat Message")],
        ondelete={"wxwork": lambda recs: recs.write({"message_type": "email"})},
    )
    notification_type = fields.Selection(
        [
            ("email", "Handle by Emails"),
            ("inbox", "Handle in Odoo"),
            ("wxwork", "Handle in Enterprise WeChat"),
        ],
        "Notification",
        required=True,
        default="email",
        help="Policy on how to handle Chatter notifications:\n"
        "- Handle by Emails: notifications are sent to your email address\n"
        "- Handle in Odoo: notifications appear in your Odoo Inbox\n"
        "- Handle in Enterprise WeChat: notifications appear in your Enterprise WeChat",
    )
    message_to_all = fields.Boolean("To all members", readonly=True,)
    message_to_user = fields.Many2many(
        "hr.employee",
        string="To Employees",
        domain="[('active', '=', True), ('is_wxwork_employee', '=', True)]",
        help="Message recipients (users)",
    )
    message_to_party = fields.Many2many(
        "hr.department",
        string="To Departments",
        domain="[('active', '=', True), ('is_wxwork_department', '=', True)]",
        help="Message recipients (departments)",
    )
    message_to_tag = fields.Many2many(
        "hr.employee.category",
        string="To Tags",
        domain="[('is_wxwork_category', '=', True)]",
        help="Message recipients (tags)",
    )
    use_templates = fields.Boolean("Test template message",)
    templates_id = fields.Many2one("wxwork.message.template", string="Message template")
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
        default="text",
    )
    body_text = fields.Text("Body")
    body_html = fields.Html("Body", sanitize=False)
    # partner_id = fields.Many2one("res.partner", "Customer")

    # state = fields.Selection(
    #     [
    #         ("outgoing", "In Queue"),
    #         ("sent", "Sent"),
    #         ("error", "Error"),
    #         ("canceled", "Canceled"),
    #     ],
    #     "SMS Status",
    #     readonly=True,
    #     copy=False,
    #     default="outgoing",
    #     required=True,
    # )

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
        help="表示是否是保密消息，0表示可对外分享，1表示不能分享且内容显示水印，2表示仅限在企业内分享，默认为0；注意仅mpnews类型的消息支持safe值为2，其他消息类型不支持",
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

    @api.onchange("use_templates")
    def _onchange_use_templates(self):
        if self.use_templates:
            self.message_to_party = None
            self.message_to_tag = None
            if len(self.message_to_user) > 1:
                raise UserError(
                    _(
                        "In the test template message mode, only one user is allowed to send."
                    )
                )
            else:
                pass
        else:
            self.body_text = None

    @api.onchange("templates_id")
    def _onchange_templates_id(self):
        if self.templates_id:
            mail_template_info = (
                self.env["wxwork.message.template"]
                .browse(self.templates_id.id)
                .read(
                    [
                        "id",
                        "subject",
                        "body_text",
                        "body_html",
                        "msgtype",
                        "safe",
                        "enable_id_trans",
                        "enable_duplicate_check",
                        "duplicate_check_interval",
                    ]
                )
            )
            self.subject = mail_template_info[0]["subject"]
            self.body_text = mail_template_info[0]["body_text"]
            self.body_html = mail_template_info[0]["body_html"]
            self.msgtype = mail_template_info[0]["msgtype"]
            self.safe = mail_template_info[0]["safe"]
            self.enable_id_trans = mail_template_info[0]["enable_id_trans"]
            self.enable_duplicate_check = mail_template_info[0][
                "enable_duplicate_check"
            ]
            self.duplicate_check_interval = mail_template_info[0][
                "duplicate_check_interval"
            ]

    def _compute_description(self):
        for message in self:
            if message.subject:
                message.description = message.subject
            else:
                plaintext_ct = (
                    ""
                    if not message.body_html
                    else tools.html2plaintext(message.body_html)
                )
                message.description = plaintext_ct[:30] + "%s" % (
                    " [...]" if len(plaintext_ct) >= 30 else ""
                )
        return super(Message, self)._compute_description()

    # ------------------------------------------------------
    # CRUD / ORM
    # ------------------------------------------------------
    @api.model_create_multi
    def create(self, values_list):
        for values in values_list:
            if "body_html" in values:
                print("body_html", values["body_html"])
        messages = super(Message, self).create(values_list)
        return messages


# -*- coding: utf-8 -*-

import logging
import re

import threading
from binascii import Error as binascii_error
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)
_image_dataurl = re.compile(
    r'(data:image/[a-z]+?);base64,([a-z0-9+/\n]{3,}=*)\n*([\'"])(?: data-filename="([^"]*)")?',
    re.I,
)


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
    is_wxwork_message = fields.Boolean("Enterprise WeChat Message")
    message_type = fields.Selection(
        selection_add=[("wxwork", "Enterprise WeChat Message")],
        ondelete={"wxwork": lambda recs: recs.write({"message_type": "email"})},
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
        default="text",
    )
    media_id = fields.Char(string="Media file id",)
    message_body_text = fields.Text("Text Body")
    message_body_html = fields.Html("Html Body", sanitize=False)

    safe = fields.Selection(
        [
            ("0", "Shareable"),
            ("1", "Cannot share and content shows watermark"),
            ("2", "Only share within the company "),
        ],
        string="Secret message",
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
        tracking_values_list = []
        for values in values_list:
            if "email_from" not in values:  # 需要计算 reply_to
                author_id, email_from = self.env["mail.thread"]._message_compute_author(
                    values.get("author_id"), email_from=None, raise_exception=False
                )
                values["email_from"] = email_from
            if not values.get("message_id"):
                values["message_id"] = self._get_message_id(values)
            if "reply_to" not in values:
                values["reply_to"] = self._get_reply_to(values)
            if (
                "record_name" not in values
                and "default_record_name" not in self.env.context
            ):
                values["record_name"] = self._get_record_name(values)

            if "attachment_ids" not in values:
                values["attachment_ids"] = []
            # 提取base64图像
            if "body" in values:
                Attachments = self.env["ir.attachment"]
                data_to_url = {}

                def base64_to_boundary(match):
                    key = match.group(2)
                    if not data_to_url.get(key):
                        name = (
                            match.group(4)
                            if match.group(4)
                            else "image%s" % len(data_to_url)
                        )
                        try:
                            attachment = Attachments.create(
                                {
                                    "name": name,
                                    "datas": match.group(2),
                                    "res_model": values.get("model"),
                                    "res_id": values.get("res_id"),
                                }
                            )
                        except binascii_error:
                            _logger.warning(
                                "Impossible to create an attachment out of badly formated base64 embedded image. Image has been removed."
                            )
                            return match.group(
                                3
                            )  # group(3) is the url ending single/double quote matched by the regexp
                        else:
                            attachment.generate_access_token()
                            values["attachment_ids"].append((4, attachment.id))
                            data_to_url[key] = [
                                "/web/image/%s?access_token=%s"
                                % (attachment.id, attachment.access_token),
                                name,
                            ]
                    return '%s%s alt="%s"' % (
                        data_to_url[key][0],
                        match.group(3),
                        data_to_url[key][1],
                    )

                values["body"] = _image_dataurl.sub(
                    base64_to_boundary, tools.ustr(values["body"])
                )
            # if "msgtype" in values:
            #     values["msgtype"]
            # 在创建后以sudo的形式委派跟踪的创建，以避免访问权限问题
            tracking_values_list.append(values.pop("tracking_value_ids", False))

        messages = super(Message, self).create(values_list)

        check_attachment_access = []
        if all(
            isinstance(command, int) or command[0] in (4, 6)
            for values in values_list
            for command in values.get("attachment_ids")
        ):
            for values in values_list:
                for command in values.get("attachment_ids"):
                    if isinstance(command, int):
                        check_attachment_access += [command]
                    elif command[0] == 6:
                        check_attachment_access += command[2]
                    else:  # command[0] == 4:
                        check_attachment_access += [command[1]]
        else:
            check_attachment_access = messages.mapped(
                "attachment_ids"
            ).ids  # fallback on read if any unknow command
        if check_attachment_access:
            self.env["ir.attachment"].browse(check_attachment_access).check(mode="read")

        for message, values, tracking_values_cmd in zip(
            messages, values_list, tracking_values_list
        ):
            if tracking_values_cmd:
                vals_lst = [
                    dict(cmd[2], mail_message_id=message.id)
                    for cmd in tracking_values_cmd
                    if len(cmd) == 3 and cmd[0] == 0
                ]
                other_cmd = [
                    cmd for cmd in tracking_values_cmd if len(cmd) != 3 or cmd[0] != 0
                ]
                if vals_lst:
                    self.env["mail.tracking.value"].sudo().create(vals_lst)
                if other_cmd:
                    message.sudo().write({"tracking_value_ids": tracking_values_cmd})

            if message.is_thread_message(values):
                message._invalidate_documents(values.get("model"), values.get("res_id"))

        return messages


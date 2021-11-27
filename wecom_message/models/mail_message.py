# -*- coding: utf-8 -*-

import logging
import re

import threading
from binascii import Error as binascii_error
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError

from datetime import datetime
from datetime import timezone
from datetime import timedelta

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
    # _name = "wecom.message"
    # _description = "Outgoing WeCom Message"
    # _rec_name = "number"
    # _order = "id DESC"

    API_TO_MESSAGE_STATE = {
        "success": "sent",
        "invaliduser": "Invalid user",
        "invalidparty": "Invalid party",
        "invalidtag": "Invalid tag",
        "api_error": "Api error",
    }
    model = fields.Char("Related Document Model", index=True)
    is_wecom_message = fields.Boolean("WeCom Message")
    message_type = fields.Selection(
        selection_add=[("wxwork", "WeCom Message")],
        ondelete={"wxwork": lambda recs: recs.write({"message_type": "email"})},
    )

    message_to_user = fields.Many2many(
        "hr.employee",
        string="To Employees",
        # domain="[('active', '=', True), ('is_wecom_employee', '=', True)]",
        help="Message recipients (users)",
    )
    message_to_party = fields.Many2many(
        "hr.department",
        string="To Departments",
        # domain="[('active', '=', True), ('is_wecom_department', '=', True)]",
        help="Message recipients (departments)",
    )
    message_to_tag = fields.Many2many(
        "hr.employee.category",
        string="To Tags",
        # domain="[('is_wecom_category', '=', True)]",
        help="Message recipients (tags)",
    )
    use_templates = fields.Boolean("Test template message", default=False)
    templates_id = fields.Many2one("wecom.message.template", string="Message template")
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
            ("template_card", "Template card message"),
        ],
        string="Message type",
        default="text",
    )
    media_id = fields.Char(
        string="Media file id",
    )
    body_json = fields.Text("Json Body", sanitize=False)
    body_html = fields.Html("Html Body", sanitize=False)
    body_markdown = fields.Text("Markdown Body", sanitize=False)

    safe = fields.Selection(
        [
            ("0", "Shareable"),
            ("1", "Cannot share and content shows watermark"),
            ("2", "Only share within the company "),
        ],
        string="Secret message",
        default="1",
        readonly=True,
        help="Indicates whether it is a confidential message, 0 indicates that it can be shared externally, 1 indicates that it cannot be shared and the content displays watermark, 2 indicates that it can only be shared within the enterprise, and the default is 0; Note that only messages of mpnews type support the safe value of 2, and other message types do not",
    )

    enable_id_trans = fields.Boolean(
        string="Turn on id translation",
        help="Indicates whether to enable ID translation, 0 indicates no, 1 indicates yes, and 0 is the default",
        default=False,
    )
    enable_duplicate_check = fields.Boolean(
        string="Turn on duplicate message checking",
        help="Indicates whether to enable duplicate message checking. 0 indicates no, 1 indicates yes. The default is 0",
        default=False,
    )
    duplicate_check_interval = fields.Integer(
        string="Time interval for repeated message checking",
        help="Indicates whether the message check is repeated. The default is 1800s and the maximum is no more than 4 hours",
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
            self.body_json = None

    @api.onchange("templates_id")
    def _onchange_templates_id(self):
        if self.templates_id:
            mail_template_info = (
                self.env["wecom.message.template"]
                .browse(self.templates_id.id)
                .read(
                    [
                        "id",
                        "subject",
                        "body_json",
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
            self.body_json = mail_template_info[0]["body_json"]
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

    def write(self, vals):
        try:
            partner_ids = self.env["res.partner"]
            if vals.get("needaction_partner_ids"):
                partner_ids |= self.env["res.partner"].browse(
                    vals["needaction_partner_ids"][0][2]
                )
            if vals.get("channel_ids"):
                channels = []
                for x in vals["channel_ids"]:
                    if x[0] == 6:
                        channels += x[2]
                channel_ids = self.env["mail.channel"].sudo().browse(channels)
                for x in channel_ids:
                    partner_ids |= x.channel_last_seen_partner_ids.mapped("partner_id")
            if partner_ids:
                record = self.env["hr.expense.config.weixin"].search([])[0]
                utc_time = datetime.today()
                today = utc_time.astimezone(timezone(timedelta(hours=+8))).strftime(
                    "%Y年%m月%d日 %H时%M分%S秒"
                )
                if ("需要您审批" not in self.body) or ("已审批完成" not in self.body):
                    for partner_id in partner_ids:
                        openid = partner_id.user_ids.wx_user.openid
                        if openid:
                            temp_id = record.template3_id
                            data = {
                                "first": {
                                    "value": "TDQM消息提醒",
                                },
                                "keyword1": {
                                    "value": self.body.strip("</p>"),
                                },
                                "keyword2": {
                                    "value": self.author_id.name,
                                },
                                "keyword3": {
                                    "value": today,
                                },
                                "remark": {
                                    "value": "",
                                },
                            }
                            record.sudo().send_message(openid, temp_id, data)
        except Exception as e:
            _logger.info("mail.message.Error: %s" % e)
        return super().write(vals)

    # ------------------------------------------------------
    # MESSAGE READ / FETCH / FAILURE API
    # 消息读取      / 获取  /   失败API
    # ------------------------------------------------------
    def _get_message_format_fields(self):
        return [
            "id",
            "body",
            "date",
            "author_id",
            "email_from",  # 基本消息字段
            "message_type",
            "subtype_id",
            "subject",  # 特定消息
            "model",
            "res_id",
            "record_name",  # 文件相关
            "channel_ids",
            "partner_ids",  # 接收者
            "starred_partner_ids",  # 为其标记消息的合作伙伴ID列表
            "moderation_status",
            # 以下为企业微信字段
            "msgtype",
            "message_to_user",
            "message_to_party",
            "message_to_tag",
            "media_id",
            "body_html",
            "body_json",
            "body_markdown",
            "safe",
            "enable_id_trans",
            "enable_duplicate_check",
            "duplicate_check_interval",
        ]

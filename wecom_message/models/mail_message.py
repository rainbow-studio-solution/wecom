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

    message_to_user = fields.Char(string="To Users", help="Message recipients (users)")
    message_to_party = fields.Char(
        string="To Departments", help="Message recipients (departments)",
    )
    message_to_tag = fields.Char(string="To Tags", help="Message recipients (tags)",)

    body_html = fields.Html("Html Contents", default="", sanitize_style=True)
    body_json = fields.Text("Json Contents", default={})
    body_markdown = fields.Text("Markdown Contents", default="")
    is_wecom_message = fields.Boolean("Is WeCom Message")
    msgtype = fields.Selection(
        [
            ("text", "Text message"),
            ("image", "Picture message"),
            ("voice", "Voice messages"),
            ("video", "Video message"),
            ("file", "File message"),
            ("textcard", "Text card message"),
            ("news", "Graphic message"),
            ("mpnews", "Graphic message(mpnews)"),
            ("markdown", "Markdown message"),
            ("miniprogram", "Mini Program Notification Message"),
            ("taskcard", "Task card message"),
            ("template_card", "Template card message"),
        ],
        string="Message type",
        default="text",
    )

    # 企业微信消息选项
    safe = fields.Selection(
        [
            ("0", "Shareable"),
            ("1", "Cannot share and content shows watermark"),
            ("2", "Only share within the company "),
        ],
        string="Secret message",
        required=True,
        default="1",
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

    # ------------------------------------------------------
    # CRUD / ORM
    # ------------------------------------------------------
    # @api.model_create_multi
    # def create(self, values_list):
    #     tracking_values_list = []
    #     # for values in values_list:
    #     #     if "message_type" not in values:
    #     #         values["message_type"] = "markdown"
    #     messages = super(Message, self).create(values_list)
    #     for message, values, tracking_values_cmd in zip(
    #         messages, values_list, tracking_values_list
    #     ):
    #         if message.is_thread_message(values):
    #             message._invalidate_documents(values.get("model"), values.get("res_id"))

    #     return super(Message, self).create(values_list)

    # ------------------------------------------------------
    # MESSAGE READ / FETCH / FAILURE API
    # 消息读取      / 获取  /   失败API
    # ------------------------------------------------------


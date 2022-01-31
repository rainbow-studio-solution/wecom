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

    # body_html = fields.Html("Html Body", translate=True, default="", sanitize=True)
    json_body = fields.Text("Json Body", translate=True, default={}, sanitize=True)
    markdown_body = fields.Text(
        "Markdown Body", translate=True, default="", sanitize=True
    )
    is_wecom_message = fields.Boolean("Is WeCom Message")

    # ------------------------------------------------------
    # CRUD / ORM
    # ------------------------------------------------------

    # ------------------------------------------------------
    # MESSAGE READ / FETCH / FAILURE API
    # 消息读取      / 获取  /   失败API
    # ------------------------------------------------------

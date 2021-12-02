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

    # ------------------------------------------------------
    # CRUD / ORM
    # ------------------------------------------------------

    # ------------------------------------------------------
    # MESSAGE READ / FETCH / FAILURE API
    # 消息读取      / 获取  /   失败API
    # ------------------------------------------------------
    @api.model
    def message_fetch(self, domain, limit=20, moderated_channel_ids=None):
        """
        Get a limited amount of formatted messages with provided domain.
        :param domain: the domain to filter messages;
        :param limit: the maximum amount of messages to get;
        :param list(int) moderated_channel_ids: if set, it contains the ID
          of a moderated channel. Fetched messages should include pending
          moderation messages for moderators. If the current user is not
          moderator, it should still get self-authored messages that are
          pending moderation;
        """

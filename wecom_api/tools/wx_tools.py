# -*- coding: utf-8 -*-

from PIL import Image
import os
import base64
import random
import html2text
import platform
import hashlib
from passlib.context import CryptContext

from odoo import api, models, tools, _
from odoo.modules.module import get_module_resource
from datetime import datetime, timedelta

import logging

_logger = logging.getLogger(__name__)


class WxTools(models.AbstractModel):
    _name = "wecom.tools"
    _description = "Wecom Tools"

    def recipients_split(text): # type: ignore
        """
        使用 | 拆分企业微信消息的接收对象
        """
        if not text:
            return []

    def wecom_user_enable(self):
        """
        企业微信用户是否启用
        :param value:
        :return:
        """
        if self.value == "0":   # type: ignore
            self.result = False
        if self.value == "1":   # type: ignore
            self.result = True
        return self.result

    def encode_avatar_image_as_base64(self, gender):
        if gender == "1":
            default_image = get_module_resource(
                "wecom_api", "static/src/img", "default_male_image.png"
            )
        elif gender == "2":
            default_image = get_module_resource(
                "wecom_api",
                "static/src/img",
                "default_female_image.png",
            )
        else:
            default_image = get_module_resource(
                "wecom_api", "static/src/img", "default_image.png"
            )

        with open(default_image, "rb") as f:
            return base64.b64encode(f.read())

    def get_default_avatar_url(self, gender):
        params = self.env["ir.config_parameter"].sudo()
        base_url = params.get_param("web.base.url")
        if gender == "1":
            default_image_url = (
                base_url + "/wecom_api/static/src/img/default_male_image.png"
            )
        elif gender == "2":
            default_image_url = (
                base_url + "/wecom_api/static/src/img/default_female_image.png"
            )

        return default_image_url    # type: ignore

    def encode_image_as_base64(self):
        if not self.value:  # type: ignore
            pass
        else:
            with open(self.value, "rb") as f:   # type: ignore
                encoded_string = base64.b64encode(f.read())
            return encoded_string

    def is_exists(self):
        """
        判断是否存在值
        :return:
        """
        if not self.value:  # type: ignore
            self.result = False
        else:
            self.result = True
        return self.result

    def mail_is_exists(self):
        """
        判断是否存在值
        :return:
        """
        if not self.value:  # type: ignore
            self.result = ""
        else:
            self.result = self.value    # type: ignore
        return self.result

# -*- coding: utf-8 -*-

from odoo import api, models, tools, _
import base64
import requests
import io
import os
import platform
import logging
from odoo.modules.module import get_module_resource

_logger = logging.getLogger(__name__)


class WecomApiToolsFile(models.AbstractModel):
    _name = "wecomapi.tools.file"
    _description = "Wecom API Tools - File"

    def path_is_exists(self, path, subpath):
        """
        检文件夹路径是否存在，不存在则创建路径
        return:返回路径
        """
        if platform.system() == "Windows":
            filepath = path.replace("\\", "/") + subpath + "/"
        else:
            filepath = path + subpath + "/"
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        return filepath

    def get_avatar_base64(self, use_default_avatar, gender, avatar_url):
        """
        获取企业微信用户头像的base64编码
        return:返回base64
        """
        imgbase64 = ""
        if use_default_avatar or avatar_url == "":
            image_name = "default_image.png"
            if gender == "1":
                image_name = "default_male_image.png"
            elif gender == "2":
                image_name = "default_female_image.png"

            default_image = get_module_resource("wecom_contacts_sync", "static/src/img", image_name)
            # print(default_image)
            with open(default_image, "rb") as f:
                imgbase64 = base64.b64encode(f.read())
        else:
            imgbase64 = base64.b64encode(requests.get(avatar_url).content)
        return imgbase64

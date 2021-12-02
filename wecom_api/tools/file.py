# -*- coding: utf-8 -*-

from odoo import api, models, tools, _
import base64
import requests
import io
import os
import platform
import logging

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

    def imgurl2base64(self, imgurl):
        """
        图片url转base64
        return:返回base64
        """
        imgbase64 = ""
        try:
            img = requests.get(imgurl)
            imgbase64 = base64.b64encode(img.content)
        except Exception as e:
            _logger.error(e)
        finally:
            return imgbase64

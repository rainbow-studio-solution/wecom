# -*- coding: utf-8 -*-

import html2text
from odoo import api, models, tools, _

class WecomApiToolsTypeConvert(models.AbstractModel):
    _name = "wecomapi.tools.convert"
    _description = "Wecom API Tools - Type convert"

    def html2text_handle(self, body_html):
        # 转换markdown格式
        if bool(body_html):
            return html2text.html2text(body_html)
        else:
            return None

    def str2bool(self):
        """
        字符串转布尔值
        :param val: 字符串
        :return: 布尔值
        """
        # return self.value.lower() in ("yes", "true", "t", "1")

        if self.value.lower() in ["true", "t", "1"]:     # type: ignore
            return True
        elif self.value.lower() in ["false", "f", "0"]:  # type: ignore
            return False
        else:
            return False

    def sex2gender(self, sex):
        """
        性别转换
        """
        if sex == "1":
            return "male"
        elif sex == "2":
            return "female"
        else:
            return "other"

    def gendge2sex(self, gender):
        if gender == "male":
            return "1"
        elif gender == "female":
            return "2"
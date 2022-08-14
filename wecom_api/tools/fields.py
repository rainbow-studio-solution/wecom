# -*- coding: utf-8 -*-

from odoo import api, models, tools, _

import logging

_logger = logging.getLogger(__name__)


class WecomApiToolsFields(models.AbstractModel):
    _name = "wecomapi.tools.fields"
    _description = "Wecom API Tools - Fields"

    def str2bool(self):
        """
        字符串转布尔值
        :param val: 字符串
        :return: 布尔值
        """
        # return self.value.lower() in ("yes", "true", "t", "1")

        if self.value.lower() in ["true", "t", "1"]:
            return True
        elif self.value.lower() in ["false", "f", "0"]:
            return False
        else:
            return False

    # def int2bool(self):
    #     """
    #     整形转布尔值
    #     :param val: 整形
    #     :return: 布尔值
    #     """
    #     if self.value.lower() in ["true", "t", "1"]:
    #         return True
    #     elif self.value.lower() in ["false", "f", "0"]:
    #         return False
    #     else:
    #         return False
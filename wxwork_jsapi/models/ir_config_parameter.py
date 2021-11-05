# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID, _
import hashlib
from ...wxwork_api.wx_qy_api.CorpApi import *
from ...wxwork_api.wx_qy_api.ErrorCode import *


class IrConfigParameter(models.Model):
    _inherit = "ir.config_parameter"

    @api.model
    def get_jsapi_param(self, args=None):
        debug = self.get_param("wxwork.jsapi_debug")
        corpid = self.get_param("wxwork.corpid")
        agentid = self.get_param("wxwork.auth_agentid")
        return {
            "parameters": [
                {
                    "debug": not not (True if debug == "True" else False),
                    "appId": corpid,
                    "agentid": agentid,
                    "signature": self.generate_signature(args),
                }
            ]
        }

    def generate_signature(self, args):
        """使用sha1加密算法，生成签名"""
        # 生成签名前，刷新ticke
        res_config = self.env["res.config.settings"].sudo()
        res_config.get_jsapi_ticket()

        url = self.get_param("web.base.url")
        ticket = self.get_param("wxwork.corp_jsapi_ticket")
        str = ("jsapi_ticket=%s&noncestr=%s&timestamp=%s&url=%s") % (
            ticket,
            args[0],
            args[1],
            url + args[2],
        )
        # print(str)
        # sha = hashlib.sha1(str.encode("utf-8"))
        # encrypts = sha.hexdigest()
        encrypts = hashlib.sha1(str.encode("utf-8")).hexdigest()
        return encrypts

    def check_ticket(self):
        """检查ticket是否有效"""

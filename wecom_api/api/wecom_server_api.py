# -*- coding: utf-8 -*-

import json
import requests
from datetime import datetime, timedelta
from odoo import api, fields, models, SUPERUSER_ID, _

# from .wecom_abstract_api import ApiException


class WecomServerApi(models.TransientModel):
    _inherit = "wecom.abstract_api"
    _name = "wecom.service_api"
    _description = "Wecom Server API"
    _table = "wecom_service_api"

    corpid = fields.Char(string="Corp Id", readonly=True)
    secret = fields.Char(string="Secret", readonly=True)
    access_token = fields.Char(string="Access Token", readonly=True, default=None)
    expiration_time = fields.Datetime(string="Expiration Time", readonly=True)

    @api.model
    def InitServiceApi(self, corpid, secret):
        """
        初始化企业微信API 对象
        :param corpid : 企业ID
        :param secret : 应用密钥
        :returns 模型"wecom.service_api"对象
        """
        api = self.search([("corpid", "=", corpid), ("secret", "=", secret),], limit=1,)

        if not api:
            # 创建API令牌记录
            api = self.sudo().create({"corpid": corpid, "secret": secret,})
        if api["access_token"] is False or api["access_token"] == "":
            # token为空，刷新API令牌记录
            api.refreshAccessToken()
        if api["expiration_time"] < datetime.now():
            # token过期，刷新API令牌记录
            api.refreshAccessToken()

        return api

    def getAccessToken(self):
        """
        获取令牌
        """
        if self.access_token is None:
            self.refreshAccessToken()
        return self.access_token

    def refreshAccessToken(self):
        """
        刷新模型 'wecom.service_api' 的令牌
        同时刷新发起请求的模型 'wecom.apps' 的令牌
        """

        response = self.httpCall(
            self.env["wecom.service_api_list"].get_server_api_call("GET_ACCESS_TOKEN"),
            {"corpid": self.corpid, "corpsecret": self.secret},
        )
        expiration_second = timedelta(seconds=response["expires_in"])

        dict = {
            "access_token": response.get("access_token"),
            "expiration_time": datetime.now() + expiration_second,
        }

        self.sudo().write(dict)

        # 写对应的应用的值
        compay_id = self.env["res.company"].search(
            [("corpid", "=", self.corpid)], limit=1
        )
        app_id = self.env["wecom.apps"].search(
            [("company_id", "=", compay_id.id), ("secret", "=", self.secret)], limit=1
        )

        app_id.sudo().write(dict)

    def get_api_debug(self):
        """
        获取 API 调试模式
        """
        ir_config = self.env["ir.config_parameter"].sudo()
        return True if ir_config.get_param("wecom.debug_enabled") == "True" else False

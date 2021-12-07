# -*- coding: utf-8 -*-

import json
import requests
from datetime import datetime, timedelta
from odoo import api, fields, models, SUPERUSER_ID, _

# from .wecom_abstract_api import ApiException


class WecomServerApi(models.Model):
    _inherit = "wecom.abstract_api"
    _name = "wecom.service_api"
    _description = "Wecom Server API"
    _table = "wecom_service_api"

    name = fields.Char(string="name", readonly=True)
    type = fields.Selection(
        [
            ("contacts", "Contacts"),
            ("external_contact", "Customer contact"),
            ("kf", "Wechat customer service"),
            ("auth", "Identity authentication"),
            ("agent", "Application management"),
            ("message", "Message push"),
            ("media", "Media material"),
            ("checkin", "Checkin"),
            ("approval", "Approval"),
            ("msgaudit", "Session content archiving"),
        ],
        string="Type",
        readonly=True,
    )
    corpid = fields.Char(string="Corp Id", readonly=True)
    secret = fields.Char(string="Secret", readonly=True)
    access_token = fields.Char(string="Access Token", readonly=True)
    expiration_time = fields.Datetime(string="Expiration Time", readonly=True)

    @api.model
    def init_api(self, company, secret_name, type_name):
        """
        初始化企业微信API 对象
        通过 secret 获取token
        :param company : 公司对象
        :param secret : secret 名称字符串
        :param token : token 名称字符串
        :returns 模型"wecom.service_api"对象
        """
        api = self.search(
            [
                ("corpid", "=", company["corpid"]),
                ("secret", "=", company[secret_name]),
            ],
            limit=1,
        )

        if not api:
            # 创建API令牌记录
            api = self.sudo().create(
                {
                    "type": type_name,
                    "corpid": company["corpid"],
                    "secret": company[secret_name],
                }
            )
            display_name = dict(
                api.fields_get(allfields=["type"])["type"]["selection"]
            )[api.type]
            api.update_api_token_name(company["name"] + "-" + display_name)
        else:
            display_name = dict(
                api.fields_get(allfields=["type"])["type"]["selection"]
            )[api.type]
            api.update_api_token_name(company["name"] + "-" + display_name)

        if api["access_token"] is False or api["access_token"] == "":
            # token为空，刷新API令牌记录
            api.refreshAccessToken()
        elif api["expiration_time"] is False or api["expiration_time"] < datetime.now():
            # expiration_time为空 或超时，刷新API令牌记录
            api.refreshAccessToken()
        return api

    def update_api_token_name(self, display_name):
        self.sudo().write(
            {
                "name": display_name,
            }
        )

    def getAccessToken(self):
        """
        获取令牌
        """
        if self.access_token is None:
            self.refreshAccessToken()
        return self.access_token

    def refreshAccessToken(self):
        """
        刷新令牌
        """
        response = self.httpCall(
            self.env["wecom.service_api_list"].get_server_api_call("GET_ACCESS_TOKEN"),
            {"corpid": self.corpid, "corpsecret": self.secret},
        )
        expiration_second = timedelta(seconds=response["expires_in"])
        self.sudo().write(
            {
                "access_token": response.get("access_token"),
                "expiration_time": datetime.now() + expiration_second,
            }
        )

    def get_api_debug(self):
        """
        获取 API 调试模式
        """
        ir_config = self.env["ir.config_parameter"].sudo()
        return True if ir_config.get_param("wecom.debug_enabled") == "True" else False

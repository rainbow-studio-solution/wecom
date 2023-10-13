# -*- coding: utf-8 -*-

import re
from odoo import api, fields, models, SUPERUSER_ID, _


class WecomServerApiList(models.Model):
    _name = "wecom.service_api_list"
    _description = "Wecom Server API List"
    _order = "sequence,type"

    type = fields.Selection(
        [
            ("1", "Base"), # 基础
            ("2", "Contacts"), # 通讯录，
            ("3", "Customer contact"), # 客户联系
            ("4", "Wechat customer service"), # 微信客服
            ("5", "Identity authentication"), # 身份验证
            ("6", "Application management"), # 应用管理
            ("7", "Message push"), # 消息推送
            ("8", "Media material"), # 媒体素材
            ("9", "OA"), # OA
            ("10", "Efficiency tools"), # 效率工具
            ("11", "externalpay"), # 企业支付
            ("12", "Corp Group"), # 企业互联
            ("13", "Corp Chain"), # 企业链，上下游
            ("14", "Session content archiving"), # 会话内容存档
            ("15", "Electronic invoice"), # 电子发票
            ("16", "School"),   # 家校沟通
            ("17", "School Apps"), # 家校应用
            ("18", "Report"),  # 政民沟通
        ],
        string="Api Type",
        required=True,
        default="GET",
    )

    name = fields.Char("Request Name", required=True,)
    function_name = fields.Char("Request Function Name", required=True, readonly=True,)

    short_url = fields.Char("Request Short Url", required=True,)

    request_type = fields.Selection(
        [("GET", "GET"), ("POST", "POST"),],
        string="Api Request Type",
        required=True,
        default="GET",
    )
    description = fields.Html(string="Description")
    sequence = fields.Integer(default=0)

    _sql_constraints = [
        ("function_name_uniq", "unique (function_name)", "The function is unique !",),
    ]

    def get_server_api_call(self, function_name):
        """
        根据函数名称获取 企业微信API的路由和请求方式
        :param function_name : 函数名称
        :returns 企业微信API的路由和请求方式的集合
        """
        # ['/cgi-bin/gettoken', 'GET']
        data = []
        res = self.search([("function_name", "=", function_name)], limit=1,)
        data.append(res.short_url)   # type: ignore
        data.append(res.request_type)    # type: ignore
        return data

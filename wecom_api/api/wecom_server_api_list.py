# -*- coding: utf-8 -*-

import re
from odoo import api, fields, models, SUPERUSER_ID, _


class WecomServerApiList(models.Model):
    _name = "wecom.service_api_list"
    _description = "Wecom Server API List"
    _order = "sequence,type"

    type = fields.Selection(
        [
            ("1", "Base"),
            ("2", "Contacts"),
            ("3", "Customer contact"),
            ("4", "Wechat customer service"),
            ("5", "Identity authentication"),
            ("6", "Application management"),
            ("7", "Message push"),
            ("8", "Media material"),
            ("9", "OA"),
            ("10", "Efficiency tools"),
            # ("meeting", "Meeting"),
            # ("living", "Living"),
            # ("wedrive", "WeDrive"),
            # ("telephone", "Telephone"),
            # ("pay", "Pay"),
            # ("corpgroup", "Corp Group"),
            # ("msgaudit", "Session content archiving"),
            # ("invoice", "Session content archiving"),
        ],
        string="Api Type",
        required=True,
        default="GET",
    )  # base:基础， contacts:通讯录， external_contact:客户联系，Servicer:微信客服，auth:身份认证， agent:应用管理,  message:消息推送,  media:媒体素材, checkin:打卡, checkin:打卡, approval:审批, worknote:汇报, meetingroom:会议室管理, schedule:日程, meeting:会议, living:直播, wedrive:微盘, telephone:公费电话, pay:企业支付, corpgroup:企业互联, msgaudit:会话内容存档, invoice:电子发票,

    name = fields.Char("Request Name", required=True, translate=True)
    function_name = fields.Char(
        "Request Function Name",
        required=True,
        readonly=True,
    )

    short_url = fields.Char(
        "Request Short Url",
        required=True,
    )

    request_type = fields.Selection(
        [
            ("GET", "GET"),
            ("POST", "POST"),
        ],
        string="Api Request Type",
        required=True,
        default="GET",
    )

    sequence = fields.Integer(default=0)

    _sql_constraints = [
        (
            "function_name_uniq",
            "unique (function_name)",
            "The function is unique !",
        ),
    ]

    def get_server_api_call(self, function_name):
        """
        根据函数名称获取 企业微信API的路由和请求方式
        :param function_name : 函数名称
        :returns 企业微信API的路由和请求方式的集合
        """
        # ['/cgi-bin/gettoken', 'GET']
        data = []
        res = self.search(
            [("function_name", "=", function_name)],
            limit=1,
        )
        data.append(res.short_url)
        data.append(res.request_type)
        return data

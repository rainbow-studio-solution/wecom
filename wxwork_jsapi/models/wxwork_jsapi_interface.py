# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID, _


class WXworkJsApiIneerface(models.Model):
    _name = "wxwork.jsapi.interface"
    _order = "name asc"
    _description = "Enterprise WeChat JSAPI Interface"

    name = fields.Char("Interface Name", required=True, translate=True)
    function_name = fields.Char("Function Name", required=True)
    type = fields.Selection(
        [
            ("base", "Basic Interface"),
            ("contacts", "Enterprise Directory"),
            ("chat", "Chat"),
            ("customer", "Customer contact"),
            ("kfchat", "Customer service"),
            ("tools", "Efficiency tools"),
            ("edu", "Education"),
            ("gov", "Political Communication"),
            ("ui", "User interface"),
            ("media", "Media"),
            ("device", "Device"),
        ],
        required=True,
        default="base",
        help="",
    )  # base:基础接口， contacts：企业通讯录， chat:会话, customer:客户联系, kfchat:客服, tools:效率工具, edu:教育, gov:政民沟通, ui:界面, media:媒体, device:设备

    example = fields.Html(string="Code example",)
    description = fields.Text("Description", required=True, translate=True)

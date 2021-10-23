# -*- coding: utf-8 -*-

import base64
from logging import info
from odoo import api, fields, models, tools, _
from odoo.modules.module import get_resource_path


class website(models.Model):
    _inherit = "website"

    def _default_technical_support_iconn(self):
        image_path = get_resource_path("website", "static/src/img", "website_logo.png")
        with tools.file_open(image_path, "rb") as f:
            return base64.b64encode(f.read())

    icp_filing_info = fields.Char("ICP Filing Info")
    isp_filing_info_text = fields.Char("Network Security Filing Info text")
    isp_filing_info_no = fields.Char("Network Security Filing Info no")
    isp_filing_info = fields.Char(
        "Network Security Filing Info", compute="_compute_isp_filing_info"
    )

    technical_support = fields.Boolean(
        "Technical Support",
        help="Display customizable technical support information on the website.",
    )
    technical_support_icon = fields.Binary(
        "Technical Support Icon", default=_default_technical_support_iconn
    )
    technical_support_name = fields.Char("Technical Support Name")
    technical_support_url = fields.Char("Technical Support Url")

    baidu_analytics_key = fields.Char("Baidu Analytics Key")
    baidu_management_client_id = fields.Char("Baidu Client ID")
    baidu_management_client_secret = fields.Char("Baidu Client Secret")
    baidu_search_console = fields.Char(
        help="Baidu key, or Enable to access first reply"
    )

    baidu_maps_api_key = fields.Char("Baidu Maps API AK")

    social_wechat = fields.Binary(
        "WeChat QR code", related="company_id.social_wechat", readonly=False,
    )

    social_wechat_kf = fields.Binary(
        "WeChat customer service QR code",
        related="company_id.social_wechat_kf",
        readonly=False,
    )
    social_wechat_kf_compute = fields.Binary(
        "WeChat customer service QR code",
        related="company_id.social_wechat_kf_compute",
        readonly=False,
    )
    social_qq = fields.Integer(
        "QQ Account", related="company_id.social_qq", readonly=False,
    )
    social_weibo = fields.Char(
        "Weibo Account url", related="company_id.social_weibo", readonly=False
    )
    social_renren = fields.Char(
        "Renren Account url", related="company_id.social_renren", readonly=False
    )

    has_social_sidebar = fields.Boolean("Enable Social Network Sidebar", default=True)

    social_sidebar_bg_color = fields.Char(
        "Social Network Sidebar Background Color", default="#ff4a00"
    )

    @api.depends("isp_filing_info_text", "isp_filing_info_no")
    def _compute_isp_filing_info(self):
        info = None
        if self.isp_filing_info_text and self.isp_filing_info_no:
            if "%s" in self.isp_filing_info_text:
                info = self.isp_filing_info_text % self.isp_filing_info_no
        self.isp_filing_info = info

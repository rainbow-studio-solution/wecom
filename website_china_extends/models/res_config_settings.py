# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    icp_filing_info = fields.Char(
        "ICP filing Info", related="website_id.icp_filing_info", readonly=False,
    )
    isp_filing_info_text = fields.Char(
        related="website_id.isp_filing_info_text", readonly=False,
    )
    isp_filing_info_no = fields.Char(
        related="website_id.isp_filing_info_no", readonly=False,
    )
    isp_filing_info = fields.Char(related="website_id.isp_filing_info",)

    technical_support = fields.Boolean(
        related="website_id.technical_support", readonly=False
    )
    technical_support_icon = fields.Binary(
        "Technical Support Icon",
        related="website_id.technical_support_icon",
        readonly=False,
    )
    technical_support_name = fields.Char(
        "Technical Support Name",
        related="website_id.technical_support_name",
        readonly=False,
    )
    technical_support_url = fields.Char(
        "Technical Support Url",
        related="website_id.technical_support_url",
        readonly=False,
    )

    baidu_analytics_key = fields.Char(
        "Baidu Analytics Key", related="website_id.baidu_analytics_key", readonly=False
    )
    baidu_management_client_id = fields.Char(
        "Baidu Client ID",
        related="website_id.baidu_management_client_id",
        readonly=False,
    )
    baidu_management_client_secret = fields.Char(
        "Baidu Client Secret",
        related="website_id.baidu_management_client_secret",
        readonly=False,
    )
    baidu_search_console = fields.Char(
        "Baidu Search Console",
        related="website_id.google_search_console",
        readonly=False,
    )

    baidu_maps_api_key = fields.Char(
        related="website_id.baidu_maps_api_key", readonly=False
    )

    social_wechat = fields.Binary(related="website_id.social_wechat", readonly=False)
    social_wechat_kf = fields.Binary(
        related="website_id.social_wechat_kf", readonly=False
    )
    social_qq = fields.Integer(related="website_id.social_qq", readonly=False)
    social_weibo = fields.Char(related="website_id.social_weibo", readonly=False)
    social_renren = fields.Char(related="website_id.social_renren", readonly=False)

    @api.depends(
        "website_id",
        "social_twitter",
        "social_facebook",
        "social_github",
        "social_linkedin",
        "social_youtube",
        "social_instagram",
        "social_wechat",
        "social_wechat_kf",
        "social_qq",
        "social_weibo",
        "social_renren",
    )
    def has_social_network(self):
        self.has_social_network = (
            self.social_twitter
            or self.social_facebook
            or self.social_github
            or self.social_linkedin
            or self.social_youtube
            or self.social_instagram
            or self.social_wechat
            or self.social_wechat_kf
            or self.social_qq
            or self.social_weibo
            or self.social_renren
        )

    def inverse_has_social_network(self):
        if not self.has_social_network:
            self.social_twitter = ""
            self.social_facebook = ""
            self.social_github = ""
            self.social_linkedin = ""
            self.social_youtube = ""
            self.social_instagram = ""
            self.social_wechat = ""
            self.social_wechat_kf = ""

            self.social_qq = ""
            self.social_weibo = ""
            self.social_renren = ""

    has_social_network = fields.Boolean(
        "Configure Social Network",
        compute=has_social_network,
        inverse=inverse_has_social_network,
    )

    has_social_sidebar = fields.Boolean(
        related="website_id.has_social_sidebar", readonly=False,
    )

    social_sidebar_bg_color = fields.Char(
        "Social Network Sidebar Background Color",
        related="website_id.social_sidebar_bg_color",
        readonly=False,
    )

    # -----------------------------------------------------
    @api.depends("website_id")
    def has_baidu_analytics(self):
        self.has_baidu_analytics = bool(self.baidu_analytics_key)

    @api.depends("website_id")
    def has_baidu_analytics_dashboard(self):
        self.has_baidu_analytics_dashboard = bool(self.baidu_management_client_id)

    @api.depends("website_id")
    def has_baidu_maps(self):
        self.has_baidu_maps = bool(self.baidu_maps_api_key)

    @api.depends("website_id")
    def has_baidu_search_console(self):
        self.has_baidu_search_console = bool(self.baidu_search_console)

    def inverse_has_baidu_analytics(self):
        if not self.has_baidu_analytics:
            self.has_baidu_analytics_dashboard = False
            self.baidu_analytics_key = False

    def inverse_has_baidu_maps(self):
        if not self.has_baidu_maps:
            self.baidu_maps_api_key = False

    def inverse_has_baidu_analytics_dashboard(self):
        if not self.has_baidu_analytics_dashboard:
            self.baidu_management_client_id = False
            self.baidu_management_client_secret = False

    def inverse_has_baidu_search_console(self):
        if not self.has_baidu_search_console:
            self.baidu_search_console = False

    # -----------------------------------------------------

    has_baidu_analytics = fields.Boolean(
        "Baidu Analytics",
        compute=has_baidu_analytics,
        inverse=inverse_has_baidu_analytics,
    )
    has_baidu_analytics_dashboard = fields.Boolean(
        "Baidu Analytics Dashboard",
        compute=has_baidu_analytics_dashboard,
        inverse=inverse_has_baidu_analytics_dashboard,
    )
    has_baidu_maps = fields.Boolean(
        "Baidu Maps", compute=has_baidu_maps, inverse=inverse_has_baidu_maps
    )
    has_baidu_search_console = fields.Boolean(
        "Console baidu Search",
        compute=has_baidu_search_console,
        inverse=inverse_has_baidu_search_console,
    )

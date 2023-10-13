# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException   # type: ignore


import werkzeug.urls
import werkzeug.utils
import urllib
import datetime
import logging

_logger = logging.getLogger(__name__)


class Company(models.Model):
    _inherit = "res.company"

    auth_app_id = fields.Many2one(
        "wecom.apps",
        string="Application",
        # required=True,
        # default=lambda self: self.env.company,
        # domain="[('company_id', '=', current_company_id)]",
        domain="[('company_id', '=', current_company_id)]",
    )

    def set_oauth_provider_wxwork(self):
        web_base_url = self.env["ir.config_parameter"].get_param("web.base.url")

        new_auth_redirect_uri = (
            urllib.parse.urlparse(web_base_url).scheme  # type: ignore
            + "://"
            + urllib.parse.urlparse(web_base_url).netloc    # type: ignore
            + urllib.parse.urlparse(self.auth_redirect_uri).path    # type: ignore
        )
        new_qr_redirect_uri = (
            urllib.parse.urlparse(web_base_url).scheme  # type: ignore
            + "://"
            + urllib.parse.urlparse(web_base_url).netloc    # type: ignore
            + urllib.parse.urlparse(self.qr_redirect_uri).path  # type: ignore
        )

        # 设置回调链接地址
        self.auth_redirect_uri = new_auth_redirect_uri
        self.qr_redirect_uri = new_qr_redirect_uri

        auth_endpoint = "https://open.weixin.qq.com/connect/oauth2/authorize"
        qr_auth_endpoint = "https://open.work.weixin.qq.com/wwopen/sso/qrConnect"

        try:
            providers = (
                self.env["auth.oauth.provider"]
                .sudo()
                .search(["|", ("enabled", "=", True), ("enabled", "=", False),])
            )
        except Exception:
            providers = []

        for provider in providers:
            if auth_endpoint in provider["auth_endpoint"]:
                provider.write(
                    {
                        # "client_id": client_id,
                        "validation_endpoint": self.auth_redirect_uri,
                        "enabled": True,
                    }
                )
            if qr_auth_endpoint in provider["auth_endpoint"]:
                provider.write(
                    {
                        # "client_id": client_id,
                        "validation_endpoint": self.qr_redirect_uri,
                        "enabled": True,
                    }
                )


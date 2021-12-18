# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException


import werkzeug.urls
import werkzeug.utils
import urllib
import datetime
import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )

    auth_app_id = fields.Many2one(related="company_id.auth_app_id", readonly=False,)
    auth_agentid = fields.Integer(related="auth_app_id.agentid", readonly=False)
    auth_secret = fields.Char(related="auth_app_id.secret", readonly=False)
    auth_access_token = fields.Char(related="auth_app_id.access_token")
    auth_app_config_ids = fields.One2many(
        # related="company_id.contacts_auto_sync_hr_enabled", readonly=False
        related="auth_app_id.app_config_ids",
        # domain="[('company_id', '=', company_id),('app_id', '=', contacts_app_id)]",
        readonly=False,
    )
    # auth_redirect_uri = fields.Char(related="company_id.auth_redirect_uri")
    # qr_redirect_uri = fields.Char(related="company_id.qr_redirect_uri")

    # enabled_join_qrcode = fields.Boolean(
    #     related="company_id.enabled_join_qrcode", readonly=False
    # )

    # join_qrcode = fields.Char(related="company_id.join_qrcode")
    # join_qrcode_size_type = fields.Selection(related="company_id.join_qrcode_size_type")

    # join_qrcode_last_time = fields.Char(related="company_id.join_qrcode_last_time")

    def set_oauth_provider_wecom(self):
        web_base_url = self.env["ir.config_parameter"].get_param("web.base.url")
        auth_redirect_uri = self.auth_app_config_ids.search(
            [("key", "=", "auth_redirect_uri")], limit=1
        )
        qr_redirect_uri = self.auth_app_config_ids.search(
            [("key", "=", "qr_redirect_uri")], limit=1
        )

        new_auth_redirect_uri = (
            urllib.parse.urlparse(web_base_url).scheme
            + "://"
            + urllib.parse.urlparse(web_base_url).netloc
            + urllib.parse.urlparse(auth_redirect_uri.value).path
        )
        new_qr_redirect_uri = (
            urllib.parse.urlparse(web_base_url).scheme
            + "://"
            + urllib.parse.urlparse(web_base_url).netloc
            + urllib.parse.urlparse(qr_redirect_uri.value).path
        )

        # 设置应用参数中的回调链接地址
        auth_redirect_uri.write({"value": new_auth_redirect_uri})
        qr_redirect_uri.write({"value": new_qr_redirect_uri})

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
                        "validation_endpoint": auth_redirect_uri,
                        "enabled": True,
                    }
                )
            if qr_auth_endpoint in provider["auth_endpoint"]:
                provider.write(
                    {
                        # "client_id": client_id,
                        "validation_endpoint": qr_redirect_uri,
                        "enabled": True,
                    }
                )


# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.wxwork_api.api.corp_api import CorpApi, CORP_API_TYPE
from odoo.addons.wxwork_api.api.abstract_api import ApiException
from odoo.addons.wxwork_api.api.error_code import Errcode

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

    auth_agentid = fields.Char(related="company_id.auth_agentid", readonly=False)

    auth_secret = fields.Char(related="company_id.auth_secret", readonly=False)

    auth_redirect_uri = fields.Char(related="company_id.auth_redirect_uri")
    qr_redirect_uri = fields.Char(related="company_id.qr_redirect_uri")

    enabled_join_qrcode = fields.Boolean(
        related="company_id.enabled_join_qrcode", readonly=False
    )

    join_qrcode = fields.Char(related="company_id.join_qrcode")
    join_qrcode_size_type = fields.Selection(related="company_id.join_qrcode_size_type")

    join_qrcode_last_time = fields.Char(related="company_id.join_qrcode_last_time")

    def set_oauth_provider_wxwork(self):
        web_base_url = self.env["ir.config_parameter"].get_param("web.base.url")

        new_auth_redirect_uri = (
            urllib.parse.urlparse(web_base_url).scheme
            + "://"
            + urllib.parse.urlparse(web_base_url).netloc
            + urllib.parse.urlparse(self.company_id.auth_redirect_uri).path
        )
        new_qr_redirect_uri = (
            urllib.parse.urlparse(web_base_url).scheme
            + "://"
            + urllib.parse.urlparse(web_base_url).netloc
            + urllib.parse.urlparse(self.company_id.qr_redirect_uri).path
        )

        # 设置回调链接地址
        self.company_id.auth_redirect_uri = new_auth_redirect_uri
        self.company_id.qr_redirect_uri = new_qr_redirect_uri

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

    def get_join_qrcode(self):
        ir_config = self.env["ir.config_parameter"].sudo()
        debug = ir_config.get_param("wxwork.debug_enabled")

        corpid = self.company_id.corpid
        secret = self.company_id.contacts_secret

        if corpid == False:
            raise UserError(_("Please fill in correctly Enterprise ID."))
        elif self.company_id.contacts_secret == False:
            raise UserError(_("Please fill in the contact Secret correctly."))
        else:
            params = {}
            if debug:
                _logger.info(_("Start getting join enterprise QR code"))
            try:
                wxapi = CorpApi(corpid, secret)
                response = wxapi.httpCall(
                    CORP_API_TYPE["GET_JOIN_QRCODE"],
                    {"size_type": self.company_id.join_qrcode_size_type,},
                )
                if response["errcode"] == 0:
                    self.company_id.join_qrcode = response["join_qrcode"]
                    self.company_id.join_qrcode_last_time = datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

                    if debug:
                        _logger.info(
                            _("Complete obtaining the QR code to join the enterprise")
                        )
                    params = {
                        "title": _("Success"),
                        "message": _("Successfully obtained the enterprise QR code."),
                        "sticky": False,  # 延时关闭
                        "className": "bg-success",
                        "next": {"type": "ir.actions.client", "tag": "reload",},  # 刷新窗体
                    }
                    action = {
                        "type": "ir.actions.client",
                        "tag": "display_notification",
                        "params": {
                            "title": params["title"],
                            "type": "success",
                            "message": params["message"],
                            "sticky": params["sticky"],
                            "next": params["next"],
                        },
                    }
                    return action
            except ApiException as ex:
                if debug:
                    _logger.info(
                        _(
                            "Failed to obtain the QR code to join the enterprise, Error code: %s, Error description: %s ,Error Details: %s"
                        )
                        % (str(ex.errCode), Errcode.getErrcode(ex.errCode), ex.errMsg)
                    )
                params = {
                    "title": _("Failed"),
                    "message": _(
                        "Error code: %s "
                        + "\n"
                        + "Error description: %s"
                        + "\n"
                        + "Error Details:"
                        + "\n"
                        + "%s"
                    )
                    % (str(ex.errCode), Errcode.getErrcode(ex.errCode), ex.errMsg),
                    "sticky": True,  # 不会延时关闭，需要手动关闭
                    "next": {},
                }
                action = {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": params["title"],
                        "type": "danger",
                        "message": params["message"],
                        "sticky": params["sticky"],  # 不会延时关闭，需要手动关闭
                        "next": params["next"],
                    },
                }
                return action

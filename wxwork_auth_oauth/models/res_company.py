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


class Company(models.Model):
    _inherit = "res.company"

    auth_agentid = fields.Char(
        "Auth agent Id",
        default="0000000",
        help="The web application ID of the authorizing party, which can be viewed in the specific web application",
    )
    auth_secret = fields.Char(
        "Auth Secret", default="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    )
    auth_redirect_uri = fields.Char(
        "Callback link address redirected after authorization",
        help="Please use urlencode to process the link",
        readonly=True,
        default="http://xxx.xxx.com:port/wxowrk_auth_oauth/authorize",
    )
    qr_redirect_uri = fields.Char(
        "Scan the QR code to log in and call back the link address",
        help="Please use urlencode to process the link",
        readonly=True,
        default="http://xxx.xxx.com:port/wxowrk_auth_oauth/qr",
    )

    enabled_join_qrcode = fields.Boolean(
        "Enable to join the enterprise QR code ", default=True
    )
    join_qrcode = fields.Char(
        "Join enterprise QR code", help="QR code link, valid for 7 days",
    )
    join_qrcode_size_type = fields.Selection(
        [("1", "171px * 171px"), ("2", "399px * 399px"), ("3", "741px * 741px"),],
        string="QR code size type",
        help="1: 171 x 171; 2: 399 x 399; 3: 741 x 741; 4: 2052 x 2052",
        default="2",
    )
    join_qrcode_last_time = fields.Char("Last update time (UTC)", readonly=True,)

    def get_join_qrcode(self):
        ir_config = self.env["ir.config_parameter"].sudo()
        debug = ir_config.get_param("wxwork.debug_enabled")

        corpid = self.corpid
        secret = self.contacts_secret

        if corpid == False:
            raise UserError(_("Please fill in correctly Enterprise ID."))
        elif self.contacts_secret == False:
            raise UserError(_("Please fill in the contact Secret correctly."))
        else:
            params = {}
            if debug:
                _logger.info(_("Start getting join enterprise QR code"))
            try:
                wxapi = CorpApi(corpid, secret)
                response = wxapi.httpCall(
                    CORP_API_TYPE["GET_JOIN_QRCODE"],
                    {"size_type": self.join_qrcode_size_type,},
                )
                if response["errcode"] == 0:
                    self.join_qrcode = response["join_qrcode"]
                    self.join_qrcode_last_time = datetime.datetime.now().strftime(
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

    def cron_get_join_qrcode(self):
        """
        获取加入企业二维码任务
        """
        ir_config = self.env["ir.config_parameter"].sudo()
        debug = ir_config.get_param("wxwork.debug_enabled")
        corpid = self.corpid
        secret = self.contacts_secret
        if corpid == False:
            if debug:
                _logger.info(_("Task error:Please fill in correctly Enterprise ID."))
        elif self.contacts_secret == False:
            if debug:
                _logger.info(
                    _("Task error:Please fill in the contact Secret correctly.")
                )
        else:
            try:
                if debug:
                    _logger.info(_("Task:Start getting join enterprise QR code"))
                wxapi = CorpApi(corpid, secret)
                response = wxapi.httpCall(
                    CORP_API_TYPE["GET_JOIN_QRCODE"],
                    {"size_type": self.join_qrcode_size_type,},
                )
                if response["errcode"] == 0:
                    self.join_qrcode = response["join_qrcode"]
                    self.join_qrcode_last_time = datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    if debug:
                        _logger.info(
                            _(
                                "Task:Complete obtaining the QR code to join the enterprise"
                            )
                        )
            except ApiException as ex:
                if debug:
                    _logger.info(
                        _(
                            "Failed to obtain the QR code to join the enterprise, Error code: %s, Error description: %s ,Error Details: %s"
                        )
                        % (str(ex.errCode), Errcode.getErrcode(ex.errCode), ex.errMsg)
                    )

    def set_oauth_provider_wxwork(self):
        web_base_url = self.env["ir.config_parameter"].get_param("web.base.url")

        new_auth_redirect_uri = (
            urllib.parse.urlparse(web_base_url).scheme
            + "://"
            + urllib.parse.urlparse(web_base_url).netloc
            + urllib.parse.urlparse(self.auth_redirect_uri).path
        )
        new_qr_redirect_uri = (
            urllib.parse.urlparse(web_base_url).scheme
            + "://"
            + urllib.parse.urlparse(web_base_url).netloc
            + urllib.parse.urlparse(self.qr_redirect_uri).path
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

    def get_company_auth_info(self, fields=None, load="_classic_read"):
        data = []
        # 获取 标记为 企业微信组织 的公司
        companies = (
            self.sudo()
            .env["res.company"]
            .search([(("is_wxwork_organization", "=", True))])
        )

        if len(companies) > 0:
            for company in companies:
                data.append(
                    {"id": company["id"], "name": company["name"],}
                )

        return data


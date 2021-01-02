# -*- coding: utf-8 -*-

import json
import requests
from odoo import models, fields, api, _
from odoo.exceptions import AccessDenied, UserError

from odoo.exceptions import except_orm, Warning, RedirectWarning, AccessDenied
from odoo.addons.auth_signup.models.res_users import SignupError

# import odoo.addons.decimal_precision as dp
import logging
from ...wxwork_api.wx_qy_api.CorpApi import CorpApi, CORP_API_TYPE

_logger = logging.getLogger(__name__)

from odoo.http import request

corpid = request.env["ir.config_parameter"].sudo().get_param("wxwork.corpid")
secret = request.env["ir.config_parameter"].sudo().get_param("wxwork.auth_secret")
auth_endpoint = "https://qyapi.weixin.qq.com/cgi-bin/user/getuserinfo"
wxwork_web_auth_endpoint = "https://open.weixin.qq.com/connect/oauth2/authorize"
wxwork_qr_auth_endpoint = "https://open.work.weixin.qq.com/wwopen/sso/qrConnect"


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def _wxwork_auth_oauth_rpc(self, endpoint, access_token, code):
        return requests.get(
            endpoint, params={"access_token": access_token, "code": code}
        ).json()

    @api.model
    def _wxwork_auth_oauth_validate(self, provider, access_token, code):
        oauth_provider = self.env["auth.oauth.provider"].browse(provider)
        validation = self._wxwork_auth_oauth_rpc(
            oauth_provider.validation_endpoint, access_token, code
        )

        if validation.get("errcode") != 0:
            raise Exception(validation["errmsg"])
        if oauth_provider.data_endpoint:
            data = self._wxwork_auth_oauth_rpc(
                oauth_provider.data_endpoint, access_token, code
            )
            validation.update(data)
        return validation

    @api.model
    def _wxwork_auth_oauth_signin(self, provider, validation, params):
        if (
            wxwork_web_auth_endpoint in provider["auth_endpoint"]
            or wxwork_qr_auth_endpoint in provider["auth_endpoint"]
        ):
            oauth_uid = validation["UserId"]
            try:
                oauth_user = self.search(
                    [
                        ("oauth_uid", "=", oauth_uid),
                        ("oauth_provider_id", "=", provider),
                    ]
                )
                if not oauth_user:
                    raise AccessDenied()
                assert len(oauth_user) == 1
                oauth_user.write({"oauth_access_token": params["access_token"]})
                return oauth_user.login
            except AccessDenied as access_denied_exception:
                if self.env.context.get("no_user_creation"):
                    return None
                state = json.loads(params["state"])
                token = state.get("t")
                values = self._generate_signup_values(provider, validation, params)
                try:
                    _, login, _ = self.signup(values, token)
                    return login
                except (SignupError, UserError):
                    raise access_denied_exception

        # return super(ResUsers, self)._auth_oauth_signin(provider, validation, params)

    @api.model
    def wxwor_auth_oauth(self, provider, c):
        wxwork_providers = (
            self.env["auth.oauth.provider"].sudo().search([("id", "=", provider),])
        )
        print(provider.auth_endpoint)
        if (
            wxwork_web_auth_endpoint in wxwork_providers["auth_endpoint"]
            or wxwork_qr_auth_endpoint in wxwork_providers["auth_endpoint"]
        ):
            wxwork_api = CorpApi(corpid, secret)
            access_token = wxwork_api.getAccessToken()
            params["access_token"] = access_token
            validation = self._wxwork_auth_oauth_validate(
                provider, access_token, params["code"]
            )
            if not validation.get("UserId"):
                raise AccessDenied()
            login = self._wxwork_auth_oauth_signin(provider, validation, params)
            if not login:
                raise AccessDenied()
            # return user credentials
            print(self.env.cr.dbname, login, access_token)
            return (self.env.cr.dbname, login, access_token)

        # return super(ResUsers, self).auth_oauth(provider, params)

    def _check_credentials(self, password, env):
        try:
            return super(ResUsers, self)._check_credentials(password, env)
        except AccessDenied:
            passwd_allowed = (
                env["interactive"] or not self.env.user._rpc_api_keys_only()
            )
            if passwd_allowed and self.env.user.active:
                res = self.sudo().search(
                    # [("id", "=", self.env.uid), ("oauth_access_token", "=", password)]
                    [("id", "=", self.env.uid), ("oauth_uid", "=", password)]
                )
                if res:
                    return
            raise

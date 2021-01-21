# -*- coding: utf-8 -*-

import json
import requests
from odoo import models, fields, api, _

from odoo.exceptions import AccessDenied

import logging

_logger = logging.getLogger(__name__)

from odoo.http import request


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def wxwrok_auth_oauth(self, provider, params):
        """
        允许一键登录和扫码登录且标记了企业微信的用户登录系统
        :param provider:
        :param params:
        :return:
        """
        wxwork_web_auth_endpoint = "https://open.weixin.qq.com/connect/oauth2/authorize"
        wxwork_qr_auth_endpoint = "https://open.work.weixin.qq.com/wwopen/sso/qrConnect"

        wxwork_providers = (
            self.env["auth.oauth.provider"].sudo().search([("id", "=", provider),])
        )

        if (
            wxwork_web_auth_endpoint in wxwork_providers["auth_endpoint"]
            or wxwork_qr_auth_endpoint in wxwork_providers["auth_endpoint"]
        ):
            # 扫码登录
            oauth_userid = params["UserId"]
            oauth_user = self.search(
                [
                    # ("oauth_uid", "=", oauth_userid),
                    ("wxwork_id", "=", oauth_userid),
                    ("is_wxwork_user", "=", True),
                    ("active", "=", True),
                ]
            )
            if not oauth_user or len(oauth_user) > 1:
                return AccessDenied
            return (self.env.cr.dbname, oauth_user.login, oauth_userid)
        else:
            return AccessDenied

    @api.model
    def _check_credentials(self, password, env):
        # password为企业微信的用户ID
        try:
            return super(ResUsers, self)._check_credentials(password, env)
        except AccessDenied:
            res = self.sudo().search(
                [("id", "=", self.env.uid), ("wxwork_id", "=", password)]
            )
            if not res:
                raise

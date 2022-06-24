# -*- coding: utf-8 -*-

from odoo import models, api, _
from odoo.exceptions import AccessDenied


class ResUsers(models.Model):
    _inherit = "res.users"

    # ---------------------
    # 验证
    # ---------------------
    @api.model
    def wecom_auth_oauth(self, provider, params):
        """
        允许一键登录和扫码登录且标记了企业微信的用户登录系统
        :param provider:
        :param params:
        :return:
        """
        wecom_web_auth_endpoint = "https://open.weixin.qq.com/connect/oauth2/authorize"
        wecom_qr_auth_endpoint = "https://open.work.weixin.qq.com/wwopen/sso/qrConnect"

        wecom_providers = (
            self.env["auth.oauth.provider"].sudo().search([("id", "=", provider),])
        )

        if (
            wecom_web_auth_endpoint in wecom_providers["auth_endpoint"]
            or wecom_qr_auth_endpoint in wecom_providers["auth_endpoint"]
        ):
            # 扫码登录
            oauth_userid = params["UserId"].lower()
            oauth_user = self.search(
                [
                    # ("oauth_uid", "=", oauth_userid),
                    ("wecom_userid", "=", oauth_userid),
                    ("is_wecom_user", "=", True),
                    ("active", "=", True),
                ]
            )
   
            if not oauth_user or len(oauth_user) > 1:
                return AccessDenied
            return (self.env.cr.dbname, oauth_user.login, oauth_userid)
        else:
            return AccessDenied


    def _check_credentials(self, password, env):
        # password为企业微信的用户ID
        try:
            return super(ResUsers, self)._check_credentials(password, env)
        except AccessDenied:
            res = self.sudo().search(
                [("id", "=", self.env.uid), ("wecom_userid", "=", password)]
            )
            if not res:
                raise

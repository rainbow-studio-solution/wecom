# -*- coding: utf-8 -*-

import werkzeug.urls
import werkzeug.utils
from odoo import models, fields, api
from ..helper.common import *


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    auth_agentid = fields.Char('应用ID', help='授权方的网页应用ID，在具体的网页应用中查看', config_parameter='wxwork.auth_agentid')
    auth_secret = fields.Char("应用的密钥", config_parameter='wxwork.auth_secret')
    auth_redirect_uri = fields.Char('授权登陆链接回调链接地址', help='授权后重定向的回调链接地址，请使用urlencode对链接进行处理',
                                    config_parameter='wxwork.auth_redirect_uri')
    qr_redirect_uri = fields.Char('扫码登陆链接回调链接地址', help='授权后重定向的回调链接地址，请使用urlencode对链接进行处理',
                                    config_parameter='wxwork.qr_redirect_uri')

    @api.multi
    def set_oauth_provider_wxwork(self):
        client_id = self.env['ir.config_parameter'].get_param('wxwork.corpid')
        auth_redirect_uri = self.env['ir.config_parameter'].get_param('wxwork.auth_redirect_uri')
        qr_redirect_uri = self.env['ir.config_parameter'].get_param('wxwork.qr_redirect_uri')

        auth_endpoint = 'https://open.weixin.qq.com/connect/oauth2/authorize'
        qr_auth_endpoint = 'https://open.work.weixin.qq.com/wwopen/sso/qrConnect'

        try:
            providers = self.env['auth.oauth.provider'].sudo().search([('enabled', '=', True)])
        except Exception:
            providers = []

        for provider in providers:
            if auth_endpoint in provider['auth_endpoint']:
                provider.write({
                    'client_id': client_id,
                    'validation_endpoint': auth_redirect_uri,
                })
            if qr_auth_endpoint in provider['auth_endpoint']:
                provider.write({
                    'client_id': client_id,
                    'validation_endpoint': qr_redirect_uri,
                })

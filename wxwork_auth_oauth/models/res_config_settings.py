# -*- coding: utf-8 -*-

import werkzeug.urls
import werkzeug.utils
from odoo import models, fields, api
from ..helper.common import *


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    auth_agentid = fields.Char('应用ID', help='授权方的网页应用ID，在具体的网页应用中查看', config_parameter='wxwork.auth_agentid')
    auth_secret = fields.Char("应用的密钥", config_parameter='wxwork.auth_secret')
    auth_redirect_uri = fields.Char('网页授权链接回调链接地址', help='授权后重定向的回调链接地址，请使用urlencode对链接进行处理',
                                    config_parameter='wxwork.auth_redirect_uri')

    @api.multi
    def set_oauth_provider_wxwork(self):
        client_id = self.env['ir.config_parameter'].get_param('wxwork.corpid')
        redirect_uri = self.env['ir.config_parameter'].get_param('wxwork.auth_redirect_uri')

        url1 = 'https://open.weixin.qq.com/connect/oauth2/authorize'
        url2 = 'https://open.work.weixin.qq.com/wwopen/sso/qrConnect'

        providers = self.env['auth.oauth.provider'].sudo().search([
            '|',
            ('auth_endpoint', '=', url1),
            ('auth_endpoint', '=', url2)
        ])

        for provider in providers:
            provider.write({
                'client_id': client_id,
                'validation_endpoint': redirect_uri,
            })



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
    # # auth_state = fields.Char('state参数', help='重定向后会带上state参数，企业可以填写a-zA-Z0-9的参数值，长度不可超过128个字节',
    #                          config_parameter='wxwork.auth_state', readonly=True, )


    # auth_link = fields.Char('网页授权链接', help='', config_parameter='wxwork.auth_link',readonly=True,)

    @api.multi
    def set_oauth_provider_wxwork(self):
        providers = self.env['auth.oauth.provider'].sudo().search_read([('enabled', '=', True)])
        for provider in providers:
            if 'https://open.weixin.qq.com/connect/oauth2/authorize' in provider['auth_endpoint']:
                pass
            elif 'https://open.work.weixin.qq.com/wwopen/sso/qrConnect' in provider['auth_endpoint']:
                pass


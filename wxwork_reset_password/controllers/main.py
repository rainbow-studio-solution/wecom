# -*- coding: utf-8 -*-

import functools
import logging

import json
import werkzeug.urls
import werkzeug.utils
from werkzeug.exceptions import BadRequest

from odoo import api, http, SUPERUSER_ID, _
from odoo.exceptions import AccessDenied
from odoo.http import request
from odoo import registry as registry_get

from odoo.addons.auth_oauth.controllers.main import OAuthLogin as Home, OAuthController as Controller
from odoo.addons.web.controllers.main import db_monodb, ensure_db, set_cookie_and_redirect, login_and_redirect

import urllib
import requests

from werkzeug import urls

from odoo.tools import ustr, consteq, frozendict, pycompat, unique

_logger = logging.getLogger(__name__)



class OAuthLogin(Home):
    def list_providers(self):
        try:
            providers = request.env['auth.oauth.provider'].sudo().search_read([('enabled', '=', True)])
        except Exception:
            providers = []
        # 构造企业微信一键登录（应用内免登录）和扫码登录链接
        for provider in providers:
            if 'https://open.weixin.qq.com/connect/oauth2/authorize' in provider['auth_endpoint']:
                return_url = request.httprequest.url_root + 'wxwork/auth_oauth/signin'
                state = self.get_state(provider)
                params = dict(
                    appid=provider['client_id'],
                    redirect_uri=return_url,
                    response_type='code',
                    scope=provider['scope'],
                    state=json.dumps(state),
                )
                provider['auth_link'] = "%s?%s%s" % (provider['auth_endpoint'], werkzeug.url_encode(params),'#wechat_redirect')
            elif 'https://open.work.weixin.qq.com/wwopen/sso/qrConnect' in provider['auth_endpoint']:
                return_url = request.httprequest.url_root + 'wxwork/auth_oauth/qr'
                state = self.get_state(provider)
                auth_agentid = request.env['ir.config_parameter'].sudo().get_param('wxwork.auth_agentid')
                params = dict(
                    appid=provider['client_id'],
                    agentid=auth_agentid,
                    redirect_uri=return_url,
                    state=json.dumps(state),
                )
                provider['auth_link'] = "%s?%s" % (provider['auth_endpoint'], werkzeug.url_encode(params))
            else:
                return_url = request.httprequest.url_root + 'auth_oauth/signin'
                state = self.get_state(provider)
                params = dict(
                    response_type='token',
                    client_id=provider['client_id'],
                    redirect_uri=return_url,
                    scope=provider['scope'],
                    state=json.dumps(state),
                )
                provider['auth_link'] = "%s?%s" % (provider['auth_endpoint'], werkzeug.url_encode(params))
        return providers

    def get_state(self, provider):
        redirect = request.params.get('redirect') or 'web'
        if not redirect.startswith(('//', 'http://', 'https://')):
            redirect = '%s%s' % (request.httprequest.url_root, redirect[1:] if redirect[0] == '/' else redirect)
        state = dict(
            d=request.session.db,
            p=provider['id'],
            r=werkzeug.url_quote_plus(redirect),
        )
        token = request.params.get('token')
        if token:
            state['t'] = token
        return state

    @http.route('/web/reset_password_wxwork', type='http', auth='public', website=True, sitemap=False)
    def web_auth_reset_password_wxwork(self, *args, **kw):
        print("微信修改密码") \

    @http.route('/web/reset_password_wxwork_qr', type='http', auth='public', website=True, sitemap=False)
    def web_auth_reset_password_wxwork_qr(self, *args, **kw):
        print("微信修改密码")


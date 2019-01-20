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
        result = super(OAuthLogin, self).list_providers()

        for provider in result:
            if 'dingtalk' in provider['auth_endpoint']:
                return_url = request.httprequest.url_root + 'dingtalk/auth_oauth/signin/' + str(provider['id'])
                state = self.get_state(provider)
                params = dict(
                    response_type='code',
                    appid=provider['client_id'],
                    redirect_uri=return_url,
                    scope=provider['scope'],
                    state='STATE',
                )
                provider['auth_link'] = "%s?%s" % (provider['auth_endpoint'], werkzeug.url_encode(params))

        return result

    @http.route('/web', type='http', auth="none")
    def web_client(self, s_action=None, **kw):
        ensure_db()
        user_agent = request.httprequest.user_agent.string.lower()

        if not request.session.uid and 'dingtalk' in user_agent:
            providers = request.env['auth.oauth.provider'].sudo().search([('auth_endpoint', 'ilike', 'dingtalk')])
            if not providers:
                return super(OAuthLogin, self).web_client(s_action, **kw)
            provider_id = providers[0].id

            icp = request.env['ir.config_parameter'].sudo()
            appid = icp.get_param('dingtalk.appid', default='')

            url = "https://oapi.dingtalk.com/connect/oauth2/sns_authorize?appid=%s&response_type=code&scope=snsapi_auth&state=STATE&redirect_uri=" % (
                appid)

            return self.redirect_dingtalk(url, provider_id)
        else:
            return super(OAuthLogin, self).web_client(s_action, **kw)

    def redirect_dingtalk(self, url, provider_id):
        url = pycompat.to_text(url).strip()
        if urls.url_parse(url, scheme='http').scheme not in ('http', 'https'):
            url = u'http://' + url
        url = url.replace("'", "%27").replace("<", "%3C")

        redir_url = "encodeURIComponent('%sdingtalk/auth_oauth/signin/%d' + location.hash.replace('#','?'))" % (
            request.httprequest.url_root, provider_id)
        return "<html><head><script>window.location = '%s' +%s;</script></head></html>" % (url, redir_url)


class OAuthController(Controller):

    @http.route('/dingtalk/auth_oauth/signin/<int:provider_id>', type='http', auth='none')
    def signin(self, provider_id, **kw):

        code = kw.get('code', "")

        action = kw.get('action', "")
        menu_id = kw.get('menu_id', "")
        model = kw.get('model', "")
        view_type = kw.get('view_type', "")

        token = self.get_token()
        openid, persistent_code = self.get_persistent_code(code, token)
        sns_token = self.get_sns_token(token, openid, persistent_code)
        userinfo = self.get_userinfo(sns_token)
        access_token = self.get_access_token()
        userid = self.get_userid_by_unionid(access_token, userinfo['unionid'])
        try:
            _logger.info("track...........")
            _logger.info("cre:%s:%s" %(str(provider_id),str(userid)))
            credentials = request.env['res.users'].sudo().auth_oauth_dingtalk(provider_id, userid)
            _logger.info("credentials: %s",credentials)
            url = '/web'

            hash = ""

            for key in kw.keys():
                if key not in ['code','state']:
                    hash+='%s=%s&' %(key,kw.get(key,""))

            if hash:
                hash = hash[:-1]
                url = '/web#' + hash

            uid = request.session.authenticate(*credentials)
            if uid is not False:
                request.params['login_success'] = True
                return http.redirect_with_hash(url)

            # resp = login_and_redirect(*credentials, url)
            # if werkzeug.urls.url_parse(resp.location).path == '/web' and not request.env.user.has_group(
            #         'base.group_user'):
            #     resp.location = '/'
            #
            # return resp
        except AttributeError:
            # auth_signup is not installed
            # _logger.error("auth_signup not installed on database %s: oauth sign up cancelled." % (dbname,))
            url = "/web/login?oauth_error=1"
        except AccessDenied:
            # oauth credentials not valid, user could be on a temporary session
            _logger.info(
                'OAuth2: access denied, redirect to main page in case a valid session exists, without setting cookies')
            url = "/web/login?oauth_error=3"
            redirect = werkzeug.utils.redirect(url, 303)
            redirect.autocorrect_location_header = False
            return redirect
        except Exception as e:
            # signup error
            _logger.exception("OAuth2: %s" % str(e))
            url = "/web/login?oauth_error=2"

    def get_token(self):
        params = request.env['ir.config_parameter'].sudo()

        appid = params.get_param('dingtalk.appid', default='')
        appscret = params.get_param('dingtalk.qr.appsecret', default='')
        if not appid or not appscret:
            raise werkzeug.exceptions.NotFound()

        params = dict(
            appid=appid,
            appsecret=appscret
        )
        url = "https://oapi.dingtalk.com/sns/gettoken"

        link = "%s?%s" % (url, werkzeug.url_encode(params))
        urlRequest = urllib.request.Request(link)
        urlResponse = urllib.request.urlopen(urlRequest).read()
        result = json.loads(str(urlResponse, encoding='utf-8'))
        if result['errcode'] == 0:
            return result['access_token']
        else:
            raise werkzeug.exceptions.BadRequest(result['errmsg'])

    def get_persistent_code(self, code, token):
        params = dict(access_token=token)
        body = {"tmp_auth_code": code}
        url = 'https://oapi.dingtalk.com/sns/get_persistent_code'
        link = "%s?%s" % (url, werkzeug.url_encode(params))

        result = requests.post(link, json=body, ).text
        result = json.loads(result)
        if result['errcode'] == 0:
            return result['openid'], result['persistent_code']
        else:
            raise werkzeug.exceptions.BadRequest(result['errmsg'])

    def get_sns_token(self, token, openid, persistent_code):
        params = dict(access_token=token)
        body = {
            "openid": openid,
            "persistent_code": persistent_code
        }
        url = 'https://oapi.dingtalk.com/sns/get_sns_token'
        link = "%s?%s" % (url, werkzeug.url_encode(params))

        result = requests.post(link, json=body, ).text
        result = json.loads(result)
        if result['errcode'] == 0:
            return result['sns_token']
        else:
            raise werkzeug.exceptions.BadRequest(result['errmsg'])

    def get_userinfo(self, sns_token):

        params = dict(sns_token=sns_token)

        url = 'https://oapi.dingtalk.com/sns/getuserinfo'

        result = requests.get(url, params).text
        result = json.loads(result)
        if result['errcode'] == 0:
            return result['user_info']
        else:
            raise werkzeug.exceptions.BadRequest(result['errmsg'])

    def get_access_token(self):
        icp = request.env['ir.config_parameter'].sudo()

        appid = icp.get_param('dingtalk.corpid', default='')
        appscret = icp.get_param('dingtalk.corpSecret', default='')
        if not appid or not appscret:
            raise werkzeug.exceptions.NotFound()

        params = dict(corpid=appid, corpsecret=appscret)

        url = "https://oapi.dingtalk.com/gettoken"
        result = requests.get(url, params)
        result = requests.get(url, params).text
        result = json.loads(result)
        if result['errcode'] == 0:
            return result['access_token']
        else:
            raise werkzeug.exceptions.BadRequest(result['errmsg'])

    def get_userid_by_unionid(self, token, unionid):
        params = dict(access_token=token, unionid=unionid)
        url = 'https://oapi.dingtalk.com/user/getUseridByUnionid'

        result = requests.get(url, params).text
        result = json.loads(result)
        if result['errcode'] == 0:
            return result['userid']
        else:
            raise werkzeug.exceptions.BadRequest(result['errmsg'])

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


from odoo.addons.auth_oauth.controllers.main import (
    OAuthLogin as Home,
    OAuthController as Controller,
    fragment_to_query_string,
)
from odoo.addons.web.controllers.main import (
    db_monodb,
    ensure_db,
    set_cookie_and_redirect,
    login_and_redirect,
)

import urllib
import requests

from werkzeug import urls

from odoo.addons.wxwork_api.api.corp_api import CorpApi, CORP_API_TYPE


_logger = logging.getLogger(__name__)


class OAuthLogin(Home):
    def list_providers(self):
        try:
            providers = (
                request.env["auth.oauth.provider"]
                .sudo()
                .search_read([("enabled", "=", True)])
            )
        except Exception:
            providers = []
        # 构造企业微信一键登录（应用内免登录）和扫码登录链接
        for provider in providers:
            if (
                "https://open.weixin.qq.com/connect/oauth2/authorize"
                in provider["auth_endpoint"]
            ):
                # 一键登录
                return_url = (
                    request.httprequest.url_root + "wxowrk_auth_oauth/authorize"
                )

                state = self.get_state(provider)
                params = dict(
                    appid=request.env["ir.config_parameter"]
                    .sudo()
                    .get_param("wxwork.corpid"),
                    redirect_uri=return_url,
                    response_type="code",
                    scope=provider["scope"],
                    state=json.dumps(state),
                )
                provider["auth_link"] = "%s?%s%s" % (
                    provider["auth_endpoint"],
                    werkzeug.urls.url_encode(params),
                    "#wechat_redirect",
                )
            elif (
                "https://open.work.weixin.qq.com/wwopen/sso/qrConnect"
                in provider["auth_endpoint"]
            ):
                # 扫描登录
                return_url = request.httprequest.url_root + "wxowrk_auth_oauth/qr"

                state = self.get_state(provider)
                auth_agentid = (
                    request.env["ir.config_parameter"]
                    .sudo()
                    .get_param("wxwork.auth_agentid")
                )
                params = dict(
                    appid=request.env["ir.config_parameter"]
                    .sudo()
                    .get_param("wxwork.corpid"),
                    agentid=auth_agentid,
                    redirect_uri=return_url,
                    state=json.dumps(state),
                )
                provider["auth_link"] = "%s?%s" % (
                    provider["auth_endpoint"],
                    werkzeug.urls.url_encode(params),
                )
            else:
                return_url = request.httprequest.url_root + "auth_oauth/signin"
                state = self.get_state(provider)
                params = dict(
                    response_type="token",
                    client_id=provider["client_id"],
                    redirect_uri=return_url,
                    scope=provider["scope"],
                    state=json.dumps(state),
                )
                provider["auth_link"] = "%s?%s" % (
                    provider["auth_endpoint"],
                    werkzeug.urls.url_encode(params),
                )
        return providers


class OAuthController(Controller):
    @http.route(
        "/wxowrk_auth_oauth/authorize", type="http", auth="none",
    )
    def wxwork_web_authorize(self, **kw):
        code = kw.pop("code", None)
        corpid = request.env["ir.config_parameter"].sudo().get_param("wxwork.corpid")
        secret = (
            request.env["ir.config_parameter"].sudo().get_param("wxwork.auth_secret")
        )
        wxwork_api = CorpApi(corpid, secret)
        response = wxwork_api.httpCall(
            CORP_API_TYPE["GET_USER_INFO_BY_CODE"], {"code": code,},
        )

        state = json.loads(kw["state"])
        dbname = state["d"]
        if not http.db_filter([dbname]):
            return BadRequest()
        provider = state["p"]
        context = {"no_user_creation": True}
        registry = registry_get(dbname)
        with registry.cursor() as cr:
            try:
                env = api.Environment(cr, SUPERUSER_ID, context)
                credentials = (
                    env["res.users"].sudo().wxwrok_auth_oauth(provider, response)
                )
                cr.commit()
                action = state.get("a")
                menu = state.get("m")
                redirect = (
                    werkzeug.urls.url_unquote_plus(state["r"])
                    if state.get("r")
                    else False
                )
                url = "/web"
                if redirect:
                    url = redirect
                elif action:
                    url = "/web#action=%s" % action
                elif menu:
                    url = "/web#menu_id=%s" % menu
                resp = login_and_redirect(*credentials, redirect_url=url)
                # Since /web is hardcoded, verify user has right to land on it
                if werkzeug.urls.url_parse(
                    resp.location
                ).path == "/web" and not request.env.user.has_group("base.group_user"):
                    resp.location = "/"
                return resp
            except AttributeError:
                # auth_signup is not installed
                _logger.error(
                    _(
                        "auth_signup not installed on database %s: oauth sign up cancelled."
                    )
                    % (dbname,)
                )
                url = "/web/login?oauth_error=1"
            except AccessDenied:
                # oauth credentials not valid, user could be on a temporary session
                _logger.info(
                    _(
                        "OAuth2: access denied, redirect to main page in case a valid session exists, without setting cookies"
                    )
                )
                url = "/web/login?oauth_error=3"
                redirect = werkzeug.utils.redirect(url, 303)
                redirect.autocorrect_location_header = False
                return redirect
            except Exception as e:
                # signup error
                _logger.exception("OAuth2: %s" % str(e))
                url = "/web/login?oauth_error=2"

        return set_cookie_and_redirect(url)

    @http.route("/wxowrk_auth_oauth/qr", type="http", auth="none")
    def wxwork_qr_authorize(self, **kw):
        code = kw.pop("code", None)
        corpid = request.env["ir.config_parameter"].sudo().get_param("wxwork.corpid")
        secret = (
            request.env["ir.config_parameter"].sudo().get_param("wxwork.auth_secret")
        )
        wxwork_api = CorpApi(corpid, secret)
        response = wxwork_api.httpCall(
            CORP_API_TYPE["GET_USER_INFO_BY_CODE"], {"code": code,},
        )

        state = json.loads(kw["state"].replace("M", '"'))
        dbname = state["d"]
        if not http.db_filter([dbname]):
            return BadRequest()
        provider = state["p"]
        context = {"no_user_creation": True}
        registry = registry_get(dbname)

        with registry.cursor() as cr:
            try:
                env = api.Environment(cr, SUPERUSER_ID, context)
                credentials = (
                    env["res.users"].sudo().wxwrok_auth_oauth(provider, response)
                )
                cr.commit()
                action = state.get("a")
                menu = state.get("m")
                redirect = (
                    werkzeug.urls.url_unquote_plus(state["r"])
                    if state.get("r")
                    else False
                )
                url = "/web"
                if redirect:
                    url = redirect
                elif action:
                    url = "/web#action=%s" % action
                elif menu:
                    url = "/web#menu_id=%s" % menu

                resp = login_and_redirect(*credentials, redirect_url=url)
                if werkzeug.urls.url_parse(
                    resp.location
                ).path == "/web" and not request.env.user.has_group("base.group_user"):
                    resp.location = "/"
                return resp
            except AttributeError:
                # auth_signup is not installed
                _logger.error(
                    "auth_signup not installed on database %s: oauth sign up cancelled."
                    % (dbname,)
                )
                url = "/web/login?oauth_error=1"
            except AccessDenied:
                # oauth credentials not valid, user could be on a temporary session
                _logger.info(
                    "OAuth2: access denied, redirect to main page in case a valid session exists, without setting cookies"
                )
                url = "/web/login?oauth_error=3"
                redirect = werkzeug.utils.redirect(url, 303)
                redirect.autocorrect_location_header = False
                return redirect
            except Exception as e:
                # signup error
                _logger.exception("OAuth2: %s" % str(e))
                url = "/web/login?oauth_error=2"

        return set_cookie_and_redirect(url)

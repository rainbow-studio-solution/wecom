# -*- coding: utf-8 -*-

# !参考 \addons\auth_oauth\controllers\main.py

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
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException   # type: ignore
from odoo.addons.auth_signup.controllers.main import AuthSignupHome as Home # type: ignore
from odoo.addons.auth_oauth.controllers.main import fragment_to_query_string    # type: ignore
from odoo.addons.web.controllers.utils import ensure_db, _get_login_redirect_url    # type: ignore

import urllib
import requests
from werkzeug import urls

_logger = logging.getLogger(__name__)

WECOM_BROWSER_MESSAGES = {
    "not_wecom_browser": _(
        "The current browser is not an WeCom built-in browser, so the one-click login function cannot be used."
    ),
    "is_wecom_browser": _(
        "It is detected that the page is opened in the built-in browser of WeCom, please select company."
    ),
}


class OAuthLogin(Home):
    def list_providers(self):
        try:
            providers = (
                request.env["auth.oauth.provider"]  # type: ignore
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
                    request.httprequest.url_root + "wxowrk_auth_oauth/authorize"    # type: ignore
                )

                state = self.get_state(provider)

                params = dict(
                    appid=False,
                    redirect_uri=return_url,
                    response_type="code",
                    scope=provider["scope"],
                    state=json.dumps(state),
                )
                provider["auth_link"] = "%s?%s%s" % (
                    provider["auth_endpoint"],
                    werkzeug.urls.url_encode(params),   # type: ignore
                    "#wechat_redirect",
                )
            elif (
                "https://open.work.weixin.qq.com/wwopen/sso/qrConnect"
                in provider["auth_endpoint"]
            ):
                # 扫描登录
                return_url = request.httprequest.url_root + "wxowrk_auth_oauth/qr"  # type: ignore

                state = self.get_state(provider)

                params = dict(
                    appid=False,
                    agentid=False,
                    redirect_uri=return_url,
                    state=json.dumps(state),
                )
                provider["auth_link"] = "%s?%s" % (
                    provider["auth_endpoint"],
                    werkzeug.urls.url_encode(params),   # type: ignore
                )
            else:
                return_url = request.httprequest.url_root + "auth_oauth/signin" # type: ignore
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


class OAuthController(http.Controller):
    @http.route(
        "/wxowrk_auth_oauth/authorize", type="http", auth="none",
    )
    @fragment_to_query_string
    def wecom_web_authorize(self, **kw):
        code = kw.pop("code", None)
        state = json.loads(kw["state"])
        company = (
            request.env["res.company"]  # type: ignore
            .sudo()
            .search(
                [("corpid", "=", state["a"]), ("is_wecom_organization", "=", True),],
            )
        )

        try:
            wxapi = (
                request.env["wecom.service_api"]    # type: ignore
                .sudo()
                .InitServiceApi(company.corpid, company.sudo().auth_app_id.secret)
            )

            # 根据code获取成员信息
            response = wxapi.httpCall(
                request.env["wecom.service_api_list"]   # type: ignore
                .sudo()
                .get_server_api_call("GET_USER_INFO_BY_CODE"),
                {"code": code,},
            )

            dbname = state["d"]
            if not http.db_filter([dbname]):
                return BadRequest()
            provider = state["p"]
            context = {"no_user_creation": True}
            registry = registry_get(dbname)
            with registry.cursor() as cr:
                try:
                    env = api.Environment(cr, SUPERUSER_ID, context)
                    db, login, key = env['res.users'].sudo().wecom_auth_oauth(provider, response)
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
                    # resp = login_and_redirect(*credentials, redirect_url=url)

                    pre_uid = request.session.authenticate(db, login, key)  # type: ignore
                    resp = request.redirect(_get_login_redirect_url(pre_uid, url), 303) # type: ignore
                    resp.autocorrect_location_header = False

                    # Since /web is hardcoded, verify user has right to land on it
                    if werkzeug.urls.url_parse(
                        resp.location
                    ).path == "/web" and not request.env.user.has_group(    # type: ignore
                        "base.group_user"
                    ):
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

            redirect = request.redirect(url, 303)   # type: ignore
            redirect.autocorrect_location_header = False
            return redirect
        except ApiException as e:
            return request.env["wecomapi.tools.action"].ApiExceptionDialog(e)   # type: ignore

    @http.route("/wxowrk_auth_oauth/qr", type="http", auth="none")
    def wecom_qr_authorize(self, **kw):
        code = kw.pop("code", None)
        company = (
            request.env["res.company"]  # type: ignore
            .sudo()
            .search(
                [("corpid", "=", kw["appid"]), ("is_wecom_organization", "=", True),],
            )
        )

        try:
            wxapi = (
                request.env["wecom.service_api"]    # type: ignore
                .sudo()
                .InitServiceApi(company.corpid, company.sudo().auth_app_id.secret)
            )
            response = wxapi.httpCall(
                request.env["wecom.service_api_list"]   # type: ignore
                .sudo()
                .get_server_api_call("GET_USER_INFO_BY_CODE"),
                {"code": code,},
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
                    db, login, key = env['res.users'].sudo().wecom_auth_oauth(provider, response)
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

                    pre_uid = request.session.authenticate(db, login, key)  # type: ignore
                    resp = request.redirect(_get_login_redirect_url(pre_uid, url), 303) # type: ignore
                    resp.autocorrect_location_header = False

                    if werkzeug.urls.url_parse(
                        resp.location
                    ).path == "/web" and not request.env.user.has_group(    # type: ignore
                        "base.group_user"
                    ):
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
            redirect = request.redirect(url, 303)   # type: ignore
            redirect.autocorrect_location_header = False
            return redirect
        except ApiException as e:
            return request.env["wecomapi.tools.action"].ApiExceptionDialog(e)   # type: ignore

    @http.route("/wxowrk_login_info", type="json", auth="none")
    def wecom_get_login_info(self, **kwargs):
        data = {}
        if "is_wecom_browser" in kwargs:
            if kwargs["is_wecom_browser"]:
                data = {
                    "is_wecom_browser": True,
                    "msg": WECOM_BROWSER_MESSAGES["is_wecom_browser"],
                    "companies": [],
                }
            else:
                data = {
                    "is_wecom_browser": False,
                    "msg": WECOM_BROWSER_MESSAGES["not_wecom_browser"],
                    "companies": [],
                }
        else:
            data = {
                "join_button_name": _("Join WeCom,Become our employee."),
                "companies": [],
            }

        # 获取 标记为 企业微信组织 的公司
        companies = request.env["res.company"].search(  # type: ignore
            [(("is_wecom_organization", "=", True))]
        )

        if len(companies) > 0:
            for company in companies:
                # app_config = request.env["wecom.app_config"].sudo()
                # contacts_app = company.contacts_app_id.sudo()  # 通讯录应用
                auth_app = company.auth_app_id.sudo()  # 验证登录应用
                data["companies"].append(
                    {
                        "id": company["id"],
                        "name": company["abbreviated_name"],
                        "fullname": company["name"],
                        "appid": company["corpid"],
                        "agentid": auth_app.agentid if auth_app else 0,
                        "enabled_join": company["wecom_contacts_join_qrcode_enabled"],
                        "join_qrcode": company["wecom_contacts_join_qrcode"],
                    }
                )
        return data

    # @http.route("/wecom_login_jsapi", type="json", auth="none")
    # def wecom_get_login_jsapi(self, **kwargs):
    #     """
    #     获取登陆页面的 JSAPI ticket
    #     args:
    #         nonceStr: 生成签名的随机串
    #         timestamp: 生成签名的时间戳
    #         url: 当前网页的URL， 不包含#及其后面部分
    #     """
    #     datas = []

    #     params = request.env["ir.config_parameter"].sudo()
    #     debug = params.get_param("wecom.jsapi_debug")

    #     # 获取 标记为 企业微信组织 的公司
    #     companies = request.env["res.company"].search(
    #         [(("is_wecom_organization", "=", True))]
    #     )
    #     if len(companies) > 0:
    #         for company in companies:
    #             data = {}
    #             parameters = {}
    #             parameters.update(
    #                 {
    #                     "beta": True,
    #                     "debug": True if debug == "True" else False,
    #                     "appId": company["corpid"],
    #                     "timestamp": kwargs["timestamp"],
    #                     "nonceStr": kwargs["nonceStr"],
    #                     "signature": request.env[
    #                         "wecomapi.tools.security"
    #                     ].generate_jsapi_signature(
    #                         company,
    #                         kwargs["nonceStr"],
    #                         kwargs["timestamp"],
    #                         kwargs["url"],
    #                     ),
    #                 }
    #             )
    #             data["id"] = company.id
    #             data["parameters"] = parameters
    #             datas.append(data)

    #     return datas

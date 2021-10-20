# -*- coding: utf-8 -*-

import functools
import logging

import json
import werkzeug.urls
import werkzeug.utils
from werkzeug.exceptions import BadRequest

from odoo import api, http, models, fields, SUPERUSER_ID, _
from odoo.http import request
from odoo.exceptions import AccessDenied, UserError

from odoo import registry as registry_get


from odoo.addons.auth_oauth.controllers.main import (
    OAuthLogin as Home,
    OAuthController as Controller,
    fragment_to_query_string,
)
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.web.controllers.main import (
    db_monodb,
    ensure_db,
    set_cookie_and_redirect,
    login_and_redirect,
)
from odoo.addons.auth_signup.controllers.main import AuthSignupHome as SignupHome

import urllib
import requests

from werkzeug import urls

from odoo.addons.wxwork_api.api.corp_api import CorpApi, CORP_API_TYPE


_logger = logging.getLogger(__name__)

WXWORK_BROWSER_MESSAGES = {
    "not_wxwork_browser": _(
        "The current browser is not an enterprise WeChat built-in browser, so the one-click login function cannot be used."
    ),
    "is_wxwork_browser": _(
        "It is detected that the page is opened in the built-in browser of enterprise wechat, please select company."
    ),
}


class AuthSignupHome(SignupHome):
    def web_auth_signup(self, *args, **kw):
        """
        消息模板用户注册帐户已创建 
        """
        qcontext = self.get_auth_signup_qcontext()

        if not qcontext.get("token") and not qcontext.get("signup_enabled"):
            raise werkzeug.exceptions.NotFound()

        if "error" not in qcontext and request.httprequest.method == "POST":
            try:
                self.do_signup(qcontext)
                # 发送帐户创建确认电子邮件
                if qcontext.get("token"):
                    User = request.env["res.users"]
                    user_sudo = User.sudo().search(
                        User._get_login_domain(qcontext.get("login")),
                        order=User._get_login_order(),
                        limit=1,
                    )

                    if not user_sudo.wxwork_id:
                        is_wxwork_message = False
                    else:
                        is_wxwork_message = True

                    template = request.env.ref(
                        "auth_signup.mail_template_user_signup_account_created",
                        raise_if_not_found=False,
                    )
                    if user_sudo and template:
                        template.sudo().send_mail(
                            user_sudo.id,
                            force_send=True,
                            is_wxwork_message=is_wxwork_message,
                        )
                return self.web_login(*args, **kw)
            except UserError as e:
                qcontext["error"] = e.args[0]
            except (SignupError, AssertionError) as e:
                if (
                    request.env["res.users"]
                    .sudo()
                    .search([("login", "=", qcontext.get("login"))])
                ):
                    qcontext["error"] = _(
                        "Another user is already registered using this email address or Enterprise WeChat id."
                    )
                else:
                    _logger.error("%s", e)
                    qcontext["error"] = _("Could not create a new account.")

        response = request.render("auth_signup.signup", qcontext)
        response.headers["X-Frame-Options"] = "DENY"
        return response

        # if "error" not in qcontext and request.httprequest.method == "POST":
        #     try:
        #         self.do_signup(qcontext)
        #         # 发送帐户创建确认电子邮件
        #         if qcontext.get("token"):
        #             User = request.env["res.users"]
        #             user_sudo = User.sudo().search(
        #                 User._get_login_domain(qcontext.get("login")),
        #                 order=User._get_login_order(),
        #                 limit=1,
        #             )

        #             if User.notification_type == "wxwork":
        #                 message_template = request.env.ref(
        #                     "wxwork_auth_oauth.message_template_user_signup_account_created",
        #                     raise_if_not_found=False,
        #                 )
        #                 if user_sudo and message_template:
        #                     message_template.sudo().send_message(
        #                         user_sudo.id, force_send=True
        #                     )
        #             else:
        #                 mail_template = request.env.ref(
        #                     "auth_signup.mail_template_user_signup_account_created",
        #                     raise_if_not_found=False,
        #                 )
        #                 if user_sudo and mail_template:
        #                     mail_template.sudo().send_mail(
        #                         user_sudo.id, force_send=True
        #                     )
        #         return self.web_login(*args, **kw)
        #     except UserError as e:
        #         qcontext["error"] = e.args[0]
        #     except (SignupError, AssertionError) as e:
        #         if (
        #             request.env["res.users"]
        #             .sudo()
        #             .search([("login", "=", qcontext.get("login"))])
        #         ):
        #             qcontext["error"] = _(
        #                 "Another user is already registered using this email address or Enterprise WeChat id."
        #             )
        #         else:
        #             _logger.error("%s", e)
        #             qcontext["error"] = _("Could not create a new account.")

        # response = request.render("auth_signup.signup", qcontext)
        # response.headers["X-Frame-Options"] = "DENY"
        # return response


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
                    appid=False,
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

                params = dict(
                    appid=False,
                    agentid=False,
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

        state = json.loads(kw["state"])

        company = (
            request.env["res.company"]
            .sudo()
            .search(
                [("corpid", "=", state["a"]), ("is_wxwork_organization", "=", True),],
            )
        )
        corpid = company.corpid
        secret = company.auth_secret
        wxwork_api = CorpApi(corpid, secret)
        response = wxwork_api.httpCall(
            CORP_API_TYPE["GET_USER_INFO_BY_CODE"], {"code": code,},
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
        company = (
            request.env["res.company"]
            .sudo()
            .search(
                [("corpid", "=", kw["appid"]), ("is_wxwork_organization", "=", True),],
            )
        )

        corpid = company.corpid
        secret = company.auth_secret
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

    @http.route("/wxowrk_login_info", type="json", auth="none")
    def wxwork_get_login_info(self, **kwargs):

        data = {}
        if "is_wxwork_browser" in kwargs:
            if kwargs["is_wxwork_browser"]:
                data = {
                    "is_wxwork_browser": True,
                    "msg": WXWORK_BROWSER_MESSAGES["is_wxwork_browser"],
                    "companies": [],
                }
            else:
                data = {
                    "is_wxwork_browser": False,
                    "msg": WXWORK_BROWSER_MESSAGES["not_wxwork_browser"],
                    "companies": [],
                }
        else:
            data = {
                "join_button_name": _("Join Enterprise WeChat,Become our employee."),
                "companies": [],
            }

        # 获取 标记为 企业微信组织 的公司
        companies = request.env["res.company"].search(
            [(("is_wxwork_organization", "=", True))]
        )

        if len(companies) > 0:
            for company in companies:
                data["companies"].append(
                    {
                        "id": company["id"],
                        "name": company["abbreviated_name"],
                        "fullname": company["name"],
                        "appid": company["corpid"],
                        "agentid": company["auth_agentid"],
                        "join_qrcode": company["join_qrcode"],
                    }
                )

        return data

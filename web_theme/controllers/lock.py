# -*- coding: utf-8 -*-

import json
import odoo
from odoo import http
from odoo.http import request
from odoo.tools.translate import _
from odoo.addons.web.controllers.utils import is_user_internal, ensure_db


UNLOCK_REQUEST_PARAMS = {
    "db",
    "login",
    "debug",
    "token",
    "message",
    "error",
    "scope",
    "mode",
    "redirect",
    "redirect_hostname",
    "email",
    "name",
    "partner_id",
    "password",
    "confirm_password",
    "city",
    "country_id",
    "lang",
    "signup_email",
}


class WebLock(http.Controller):
    @http.route(
        "/web/lockscreen",
        type="json",
        auth="user",
        website=True,
    )
    def lockscreen(self, uid, lock_screen_info):
        result = {}
        session_info = request.env["ir.http"].session_info()
        frontend_session_info = request.env["ir.http"].get_frontend_session_info()

        storage_mode = session_info["lock_screen_state_storage_mode"]
        lock = {
            "uid": uid,
            "href": lock_screen_info["href"],
            "host": lock_screen_info["host"],
            "pathname": lock_screen_info["pathname"],
            "search": lock_screen_info["search"],
            "hash": lock_screen_info["hash"],
        }
        # if "lock" in lock_screen_info:
        #     lock["lock"] = lock_screen_info["lock"]

        try:
            # if storage_mode ==1:
            #     session_info.update({"lock_screen_state": True})
            #     frontend_session_info.update({"lock_screen_state": True})
            if storage_mode == 2:
                user = self.env["res.users"].sudo().search([("id", "=", uid)], limit=1)
        except Exception as e:
            result.update(
                {
                    "state": False,
                    "msg": str(e),
                }
            )
            return {
                "state": False,
            }
        else:
            if storage_mode == 2:
                user.write({"lock_screen": True})

            lock["state"] = True  # 更新 lock_screen_session_info["state"] 为 True
            request.session["lock_screen_session_info"] = json.loads(json.dumps(lock))
            request.session.modified = True  # 标记session已修改
            result.update(
                {
                    "state": True,
                    "msg": "",
                    "storage_mode": storage_mode,
                    "lock_screen_state": True,
                }
            )
        finally:
            return result

    def _prepare_lock_layout_values(self):
        lock_user_sudo = request.env.user
        # partner_sudo = request.env.user.partner_id

        return {
            "lock_user": lock_user_sudo,
        }

    @http.route(
        "/web/lock",
        type="http",
        auth="user",
        website=True,
    )
    def lock_client(self, **kw):
        """
        锁屏
        """
        if "lock_screen_session_info" in request.session:
            lock_screen_session_info = request.session["lock_screen_session_info"]
            lock_screen_state = lock_screen_session_info["state"]

        values = self._prepare_lock_layout_values()
        if "lock_screen_session_info" in request.session:
            lock_screen_session_info = request.session["lock_screen_session_info"]
            request.session.modified = True  # 标记session已修改
            values.update(**lock_screen_session_info)

        session_info = request.env["ir.http"].session_info()
        # print(session_info)
        storage_mode = session_info["lock_screen_state_storage_mode"]
        lock_screen = request.env["res.users"].browse(request.session.uid).lock_screen
        if (
            request.session.uid
            and is_user_internal(request.session.uid)
            and not lock_screen
            and storage_mode == 2
        ):
            if lock_screen_session_info["href"]:
                return request.redirect(lock_screen_session_info["href"])
            else:
                return request.redirect_query("/web", "")
        if storage_mode == 1:
            if not lock_screen_state:
                if lock_screen_session_info["href"]:
                    return request.redirect(lock_screen_session_info["href"])
                else:
                    return request.redirect_query("/web", "")

        response = request.render("web_theme.lock", values)
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["Content-Security-Policy"] = "frame-ancestors 'self'"

        return response

    @http.route(
        "/web/unlock",
        type="json",
        auth="user",
        website=True,
        methods=["POST", "GET"],
    )
    def web_unlock(self):
        """
        解锁
        """
        ensure_db()

        session_info = request.env["ir.http"].session_info()
        storage_mode = session_info["lock_screen_state_storage_mode"]
        lock_screen_session_info = request.session["lock_screen_session_info"]

        values = {k: v for k, v in request.params.items() if k in UNLOCK_REQUEST_PARAMS}
        values = self._prepare_lock_layout_values()
        values.update(**lock_screen_session_info, storage_mode=storage_mode)

        if request.httprequest.method == "POST":
            try:
                uid = request.session.authenticate(
                    request.db, request.params["login"], request.params["password"]
                )
                values["message"] = _("The password is correct, unlocking...")
                if storage_mode == 1:
                    session_info["lock_screen_state"] = False
                if storage_mode == 2:
                    user = (
                        request.env["res.users"]
                        .sudo()
                        .search([("id", "=", uid)], limit=1)
                    )
                    user.write({"lock_screen": False})
                request.session["lock_screen_session_info"]["state"] = False
                request.session.modified = True  # 标记session已修改
            except odoo.exceptions.AccessDenied as e:
                if e.args == odoo.exceptions.AccessDenied().args:
                    values["error"] = _("Wrong password")
                else:
                    values["error"] = e.args[0]
        else:
            if "error" in request.params and request.params.get("error") == "access":
                values["error"] = _(
                    "Only employees can access this database. Please contact the administrator."
                )
        return values

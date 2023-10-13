# -*- coding: utf-8 -*-

import json
import logging
from pickle import TRUE


from odoo import http
from odoo.exceptions import AccessError
from odoo.http import request
from odoo.addons.web.controllers.home import Home as WebHome
from odoo.addons.web.controllers.utils import is_user_internal,ensure_db



class Home(WebHome):
    @http.route()
    def web_client(self, s_action=None, **kw):
        ensure_db()
        if not request.session.uid:
            return request.redirect('/web/login', 303)
        storage_mode = int(request.env['res.users'].browse(request.session.uid).company_id.lock_screen_state_storage_mode)

        if "lock_screen_session_info" in request.session:
            lock_screen_session_info = request.session["lock_screen_session_info"]
            lock_screen_state = lock_screen_session_info["state"]
        else:
            lock_screen_state = False

        if storage_mode == 1:
            if lock_screen_state:
                return request.redirect('/web/lock', 303)
            # return request.redirect_query("/web/lock", "")
        elif storage_mode == 2:
            lock_screen = request.env["res.users"].browse(request.session.uid).lock_screen
            if (
                request.session.uid
                and is_user_internal(request.session.uid)
                and lock_screen
            ):
                return request.redirect_query("/web/lock", "")
        return super().web_client(s_action, **kw)

    @http.route("/web/lang/toggle", type="json", auth="user")
    def toggle_web_lang(self, lang):
        uid = dict(request.context)["uid"]
        if not uid:
            return False

        user = request.env["res.users"].browse(uid)
        try:
            user.sudo().write({"lang": lang["code"]})
        except Exception as e:
            print(str(e))
            return False
        else:
            session_info = request.env["ir.http"].session_info()
            session_info["current_lang"] = lang
            return True

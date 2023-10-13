# -*- coding: utf-8 -*-

import odoo
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.session import Session as WebSession

class Session(WebSession):
    @http.route()
    def logout(self, redirect='/web'):
        storage_mode = int(request.env['res.users'].browse(request.session.uid).company_id.lock_screen_state_storage_mode)
        if request.session.uid and storage_mode == 2:
            request.env['res.users'].sudo().browse(request.session.uid).write({'lock_screen': False})
        return super(Session, self).logout(redirect)
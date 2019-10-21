#!/usr/bin/python
# -*- coding:utf-8 -*-

from odoo import api, http, SUPERUSER_ID, _
from odoo.http import request
from odoo.addons.web.controllers.main import db_monodb, ensure_db, set_cookie_and_redirect, login_and_redirect

## 设置为true会打印一些调试信息

class DebugMode(http.Controller):
    def get_wxwork_debug(self, **kw):
        pass

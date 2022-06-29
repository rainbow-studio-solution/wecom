# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from odoo import _, api, fields, models

MENU_BODY = {
    "button": [{"id": "portal", "type": "view", "name": "My Portal", "url": ""}]
}


class WeComApps(models.Model):
    _inherit = "wecom.apps"

    menu_body = fields.Text("Application menu data", translate=True, default={})

    def set_wecom_app_menu(self):
        """
        设置企业微信应用菜单
        """
        web_base_url = self.env["ir.config_parameter"].get_param("web.base.url")
        print(MENU_BODY["button"])

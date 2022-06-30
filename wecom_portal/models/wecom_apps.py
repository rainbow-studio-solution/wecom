# -*- coding: utf-8 -*-

import json
from datetime import datetime, timedelta
from odoo import _, api, fields, models
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException

MENU_TEMPLATE = {
    "button": [{"id": "portal", "type": "view", "name": "My Portal", "url": ""}]
}


class WeComApps(models.Model):
    _inherit = "wecom.apps"

    menu_body = fields.Text("Application menu data", translate=True, default="{}")

    def set_wecom_app_menu(self):
        """
        设置企业微信应用菜单
        """

        web_base_url = self.env["ir.config_parameter"].get_param("web.base.url")
        menu = {}
        if self.menu_body == "":
            self.menu_body = json.dumps(MENU_TEMPLATE)
        if (
            eval(self.menu_body)
            and "button" in eval(self.menu_body)
            and eval(self.menu_body)["button"]
        ):
            # menu_body 不为空  +  存在 button 列表   +   button 列表元素大于一
            menu = eval(self.menu_body)
        else:
            # menu_body 为空
            menu = MENU_TEMPLATE

        for button in menu["button"]:
            if "id" in button and button["id"] == "portal":
                # button["url"] = web_base_url+"/my"
                button.update(
                    {
                        "type": "view",
                        "name": _("My Portal"),
                        "url": web_base_url + "/my",
                    }
                )
                del button["id"]

        self.menu_body = json.dumps(
            menu, sort_keys=True, indent=4, separators=(",", ":")
        )
        try:
            wxapi = self.env["wecom.service_api"].InitServiceApi(
                self.company_id.corpid, self.secret,
            )
            menu.update({"agentid": str(self.agentid)})
            response = wxapi.httpCall(
                self.env["wecom.service_api_list"].get_server_api_call("MENU_CREATE"),
                menu,
                include_agentid=True,
            )
            if response["errcode"] == 0:
                message = {
                    "title": _("success!"),
                    "message": _("Set application menu successfully!"),
                    "sticky": False,
                }
                return {"state": True, "msg": message, "body": self.menu_body}

        except ApiException as ex:
            return {"state": False, "msg": ex}


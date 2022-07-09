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

    

    def get_wecom_app_menu(self):
        """
        获取企微应用菜单 MENU_GET
        """
        try:
            wxapi = self.env["wecom.service_api"].InitServiceApi(
                self.company_id.corpid, self.secret,
            )

            response = wxapi.httpCall(
                self.env["wecom.service_api_list"].get_server_api_call("MENU_GET"),
                {"agentid": str(self.agentid)},
            )

            if response["errcode"] == 0:
                message = {
                    "title": _("success!"),
                    "message": _("Get application menu successfully!"),
                    "sticky": False,
                }
                body = {"button": response["button"]}

                return {
                    "state": True,
                    "msg": message,
                    "body": json.dumps(
                        body,
                        sort_keys=False,
                        indent=2,
                        separators=(",", ":"),
                        ensure_ascii=False,
                    ),
                }

        except ApiException as ex:
            return {"state": False, "msg": ex}

    def set_wecom_app_menu(self):
        """
        设置企业微信应用菜单
        """

        web_base_url = self.env["ir.config_parameter"].get_param("web.base.url")
        menu = {}
        if self.menu_body == "":
            self.menu_body = json.dumps(
                MENU_TEMPLATE,
                sort_keys=False,
                indent=2,
                separators=(",", ":"),
                ensure_ascii=False,
            )
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
                button.update(
                    {
                        "type": "view",
                        "name": _("My Portal"),
                        "url": web_base_url + "/my",
                    }
                )
                del button["id"]

        try:
            wxapi = self.env["wecom.service_api"].InitServiceApi(
                self.company_id.corpid, self.secret,
            )
            menu.update({"agentid": str(self.agentid)})
            response_set = wxapi.httpCall(
                self.env["wecom.service_api_list"].get_server_api_call("MENU_CREATE"),
                menu,
                include_agentid=True,
            )
            response_get = wxapi.httpCall(
                self.env["wecom.service_api_list"].get_server_api_call("MENU_GET"),
                {"agentid": str(self.agentid)},
            )

            if response_get["errcode"] == 0:
                body = {"button": response_get["button"]}
                self.menu_body = json.dumps(
                    body,
                    sort_keys=False,
                    indent=2,
                    separators=(",", ":"),
                    ensure_ascii=False,
                )
                message = {
                    "title": _("success!"),
                    "message": _("Set application menu successfully!"),
                    "sticky": False,
                }
                return {"state": True, "msg": message, "body": self.menu_body}

        except ApiException as ex:
            return {"state": False, "msg": ex}

    def delete_wecom_app_menu(self):
        """
        删除企微应用菜单
        """
        try:
            wxapi = self.env["wecom.service_api"].InitServiceApi(
                self.company_id.corpid, self.secret,
            )

            response = wxapi.httpCall(
                self.env["wecom.service_api_list"].get_server_api_call("MENU_DELETE"),
                {"agentid": str(self.agentid)},
            )

            if response["errcode"] == 0:
                message = {
                    "title": _("success!"),
                    "message": _("Delete application menu successfully!"),
                    "sticky": False,
                }
                return {
                    "state": True,
                    "msg": message,
                }

        except ApiException as ex:
            return {"state": False, "msg": ex}

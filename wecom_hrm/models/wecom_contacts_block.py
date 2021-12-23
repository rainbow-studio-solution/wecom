# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException


class WxworkContactsBlock(models.Model):
    _name = "wecom.contacts.block"
    _description = "Wecom contacts synchronization block list"

    name = fields.Char(
        string="Name", readonly=True,
    )  # required=True,readonly=True, store=True
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        domain="[('is_wecom_organization', '=', True)]",
        copy=False,
        required=True,
    )

    wecom_userid = fields.Char(string="WeCom user Id", required=True)

    def get_name(self):
        if self.company_id is None or self.wecom_userid == False:
            return
        try:
            wxapi = self.env["wecom.service_api"].InitServiceApi(
                self.company_id, "contacts_secret", "contacts"
            )
            response = wxapi.httpCall(
                self.env["wecom.service_api_list"].get_server_api_call("USER_GET"),
                {"userid": self.wecom_userid},
            )

            params = {}
            if "errcode" in str(response):
                if response["errcode"] == 0:
                    self.name = response["name"]

                    params = {
                        "title": _("Success"),
                        "type": "success",
                        "className": "bg-success",
                        "message": _("Get user name successfully"),
                        "sticky": False,  # 延时关闭
                        "next": {},
                    }

            else:
                self.name = ""
                params = {
                    "title": _("Failed"),
                    "type": "danger",
                    "className": "bg-danger",
                    "message": _("Failed to read WeCom members! Error details: %s .")
                    % (str(response)),
                    "sticky": True,  # 不会延时关闭，需要手动关闭
                    "next": {},
                }
                # self.write({"name": ""})

            action = {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": params["title"],
                    "type": params["type"],
                    "className": params["className"],
                    "message": params["message"],
                    "sticky": params["sticky"],
                    "next": {"type": "ir.actions.client", "tag": "reload",},  # 刷新窗体
                },
            }
            return action
        except ApiException as ex:
          return self.env["wecomapi.tools.action"].ApiExceptionDialog(
                    ex, raise_exception=True
                )

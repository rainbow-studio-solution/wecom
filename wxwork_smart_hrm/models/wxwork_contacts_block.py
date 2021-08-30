# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.wxwork_api.api.corp_api import CorpApi, CORP_API_TYPE
from odoo.addons.wxwork_api.api.abstract_api import ApiException
from odoo.addons.wxwork_api.api.error_code import Errcode


class WxworkContactsBlock(models.Model):
    _name = "wxwork.contacts.block"

    name = fields.Char(
        string="Name", readonly=True,
    )  # required=True,readonly=True, store=True
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        domain="[('is_wxwork_organization', '=', True)]",
        copy=False,
    )

    wxwork_id = fields.Char(string="Enterprise WeChat user Id")

    def get_name(self):
        if self.company_id is None or self.wxwork_id == False:
            return
        wxapi = CorpApi(self.company_id.corpid, self.company_id.contacts_secret)

        response = wxapi.httpCall(
            CORP_API_TYPE["USER_GET"], {"userid": self.wxwork_id},
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
                "message": _(
                    "Failed to read enterprise wechat members! Error details: %s ."
                )
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

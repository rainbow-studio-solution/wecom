# -*- coding: utf-8 -*-

from odoo.addons.wxwork_api.api.corp_api import CorpApi, CORP_API_TYPE
from odoo.addons.wxwork_api.api.abstract_api import ApiException
from odoo.addons.wxwork_api.api.error_code import Errcode

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError
from ..models.sync_contacts import *
import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    def get_contacts_access_token(self):
        ir_config = self.env["ir.config_parameter"].sudo()
        corpid = ir_config.get_param("wxwork.corpid")
        secret = ir_config.get_param("wxwork.contacts_secret")
        # debug = ir_config.get_param("wxwork.debug_enabled")
        if corpid == False:
            raise UserError(_("Please fill in correctly Enterprise ID."))
        elif (
            "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" in secret
            or self.contacts_secret == False
        ):
            raise UserError(_("Please fill in the contact Secret correctly."))
        else:
            params = {}
            wxapi = CorpApi(corpid, secret)
            try:
                response = wxapi.httpCall(
                    CORP_API_TYPE["GET_ACCESS_TOKEN"],
                    {"corpid": corpid, "corpsecret": secret,},
                )
                if "errcode" in str(response):
                    if response["errcode"] == 0:
                        params = {
                            "title": _("Success"),
                            "message": _(
                                "Successfully obtained corporate WeChat contact token."
                            ),
                            "sticky": False,  # 延时关闭
                            "className": "bg-success",
                            "next": {
                                "type": "ir.actions.client",
                                "tag": "reload",
                            },  # 刷新窗体
                        }
                        self.env["ir.config_parameter"].sudo().set_param(
                            "wxwork.contacts_access_token", wxapi.getAccessToken()
                        )
                        action = {
                            "type": "ir.actions.client",
                            "tag": "display_notification",
                            "params": {
                                "title": params["title"],
                                "type": "success",
                                "message": params["message"],
                                "sticky": params["sticky"],
                                "next": params["next"],
                            },
                        }
                        return action
                else:
                    raise UserError(_("Please fill in the contact Secret correctly."))

            except ApiException as ex:
                params = {
                    "title": _("Failed"),
                    "message": _(
                        "Error code: %s "
                        + "\n"
                        + "Error description: %s"
                        + "\n"
                        + "Error Details:"
                        + "\n"
                        + "%s"
                    )
                    % (str(ex.errCode), Errcode.getErrcode(ex.errCode), ex.errMsg),
                    "sticky": True,  # 不会延时关闭，需要手动关闭
                    "next": {},
                }
                action = {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        # "className": "wxwork_config_notification",
                        "title": params["title"],
                        "type": "danger",
                        "message": params["message"],
                        "sticky": params["sticky"],  # 不会延时关闭，需要手动关闭
                        "next": params["next"],
                    },
                }
                return action

    
# -*- coding: utf-8 -*-

from odoo.addons.wecom_api.api.corp_api import CorpApi, CORP_API_TYPE
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException
from odoo.addons.wecom_api.api.error_code import Errcode


from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import datetime
import time
import json
import platform
import logging


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    attendance_secret = fields.Char(
        "Attendance Secret", config_parameter="wecom.attendance_secret"
    )
    attendance_access_token = fields.Char(
        "Attendance Token",
        config_parameter="wecom.attendance_access_token",
        readonly=True,
    )

    def get_attendance_access_token(self):
        if self.corpid == False:
            raise UserError(_("Please fill in correctly Enterprise ID."))
        elif self.contacts_secret == False:
            raise UserError(_("Please fill in the check-in Secret correctly."))
        else:
            params = {}

            try:
                wxapi = CorpApi(self.corpid, self.attendance_secret)
                params = {
                    "title": _("Success"),
                    "message": _(
                        "Successfully obtained corporate WeChat check-in token."
                    ),
                    "sticky": False,  # 延时关闭
                    "className": "bg-success",
                    "next": {
                        "type": "ir.actions.client",
                        "tag": "reload",
                    },  # 刷新窗体
                }
                self.env["ir.config_parameter"].sudo().set_param(
                    "wecom.attendance_access_token", wxapi.getAccessToken()
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
                        # "className": "wecom_config_notification",
                        "title": params["title"],
                        "type": "danger",
                        "message": params["message"],
                        "sticky": params["sticky"],  # 不会延时关闭，需要手动关闭
                        "next": params["next"],
                    },
                }
                return action

    def cron_pull_attendance_data(self):
        pass

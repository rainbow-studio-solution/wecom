# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError

from odoo.addons.wxwork_api.api.corp_api import CorpApi, CORP_API_TYPE
from odoo.addons.wxwork_api.api.abstract_api import ApiException
from odoo.addons.wxwork_api.api.error_code import Errcode


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )

    def get_contacts_access_token(self):

        corpid = self.company_id.corpid
        secret = self.company_id.contacts_secret

        if corpid == False:
            raise UserError(_("Please fill in correctly Enterprise ID."))
        elif (
            "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" in secret
            or self.company_id.contacts_secret == False
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

                        self.company_id.contacts_access_token = wxapi.getAccessToken()

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

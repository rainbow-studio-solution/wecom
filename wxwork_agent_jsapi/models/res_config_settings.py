# -*- coding: utf-8 -*-

from ...wxwork_api.CorpApi import *
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
import time


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    auth_agentid = fields.Char(
        "Agent Id",
        help="The web application ID of the authorizing party, which can be viewed in the specific web application",
        config_parameter="wxwork.auth_agentid",
    )
    auth_secret = fields.Char(
        "Secret",
        config_parameter="wxwork.auth_secret",
    )

    agent_jsapi_ticket = fields.Char(
        "Application JS API Ticket",
        config_parameter="wxwork.agent_jsapi_ticket",
    )

    def get_agent_jsapi_ticket(self):
        res = super(ResConfigSettings, self).get_values()

        ir_config = self.env["ir.config_parameter"].sudo()
        corpid = ir_config.get_param("wxwork.corpid")
        if corpid == False:
            raise UserError(_("Please fill in correctly Enterprise ID."))
        elif self.auth_secret == False:
            raise UserError(_("Please fill in the application 'secret' correctly."))

        else:
            api = CorpApi(self.corpid, self.auth_secret)
            try:
                response = api.httpCall(
                    CORP_API_TYPE["GET_TICKET"],
                    {
                        "access_token": api.getAccessToken(),
                        "type": "agent_config",
                    },
                )
                if self.agent_jsapi_ticket != response["ticket"]:
                    ir_config.set_param("wxwork.agent_jsapi_ticket", response["ticket"])

            except ApiException as ex:
                pass

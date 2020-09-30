# -*- coding: utf-8 -*-

import logging
from ...wxwork_api.wx_qy_api.CorpApi import *
from ...wxwork_api.wx_qy_api.ErrorCode import *
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from odoo.exceptions import Warning
import time

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # auth_agentid = fields.Char(
    #     "Agent Id",
    #     help="The web application ID of the authorizing party, which can be viewed in the specific web application",
    # )
    # auth_secret = fields.Char(
    #     "Secret",
    # )

    agent_jsapi_ticket = fields.Char(
        "Application JS API Ticket",
        config_parameter="wxwork.agent_jsapi_ticket",
    )

    # @api.model
    # def get_values(self):
    #     res = super(ResConfigSettings, self).get_values()
    #     ir_config = self.env["ir.config_parameter"].sudo()

    #     auth_agentid = ir_config.get_param("wxwork.auth_agentid")
    #     auth_secret = ir_config.get_param("wxwork.auth_secret")

    #     res.update(
    #         auth_agentid=auth_agentid,
    #         auth_secret=auth_secret,
    #     )
    #     return res

    def cron_pull_application_ticket(self):
        ir_config = self.env["ir.config_parameter"].sudo()
        corpid = ir_config.get_param("wxwork.corpid")
        auth_secret = ir_config.get_param("wxwork.auth_secret")
        api = CorpApi(corpid, auth_secret)
        try:
            response = api.httpCall(
                CORP_API_TYPE["GET_TICKET"],
                {
                    "access_token": api.getAccessToken(),
                    "type": "agent_config",
                },
            )

            if response["errcode"] == 0:
                if self.agent_jsapi_ticket != response["ticket"]:
                    ir_config.set_param(
                        "wxwork.agent_jsapi_ticket", response["ticket"])
                _logger.info(
                    _(
                        "Timed task:Successfully pull the enterprise WeChat application ticket regularly"
                    )
                )
            else:
                _logger.warning(
                    _(
                        "Timed task:Failed to pull the enterprise WeChat application ticket regularly"
                    )
                )
        except ApiException as ex:
            _logger.warning(
                _(
                    "Timed task:Failed to pull the enterprise WeChat application ticket regularly. Error code: %s"
                    % ex.errCode
                )
            )

    def get_agent_jsapi_ticket(self):
        ir_config = self.env["ir.config_parameter"].sudo()
        corpid = ir_config.get_param("wxwork.corpid")
        auth_secret = ir_config.get_param("wxwork.auth_secret")
        if corpid == False:
            raise UserError(_("Please fill in correctly Enterprise ID."))
        elif auth_secret == False:
            raise UserError(
                _("Please fill in the application 'secret' correctly."))

        else:
            api = CorpApi(corpid, auth_secret)
            try:

                response = api.httpCall(
                    CORP_API_TYPE["GET_TICKET"],
                    {
                        "access_token": api.getAccessToken(),
                        "type": "agent_config",
                    },
                )
                message = {}
                if response["errcode"] == 0:
                    if self.agent_jsapi_ticket != response["ticket"]:
                        ir_config.set_param(
                            "wxwork.agent_jsapi_ticket", response["ticket"]
                        )

                        return {
                            'type': 'ir.actions.client',
                            'tag': 'dialog',
                            'params': {
                                'title': _("Successful operation"),
                                '$content':  _('<div>Successfully pull the enterprise WeChat application ticket regularly.</div>'),
                                'size': 'medium',
                            }
                        }

                    else:
                        return {
                            'type': 'ir.actions.client',
                            'tag': 'dialog',
                            'params': {
                                'title': _("Successful operation"),
                                '$content':  _('<div>The enterprise WeChat application ticket is within the validity period and does not need to be pulled.</div>'),
                                'size': 'medium',
                            }
                        }
            except ApiException as ex:
                raise UserError(
                    _("Error code: %s \nError description: %s \nError Details:\n%s")
                    % (str(ex.errCode), Errcode.getErrcode(ex.errCode), ex.errMsg)
                )

    def generate_signature(self):
        pass

# -*- coding: utf-8 -*-

import logging
from ...wxwork_api.wx_qy_api.CorpApi import *
from ...wxwork_api.wx_qy_api.ErrorCode import *
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

import datetime
import time

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    corp_jsapi_ticket = fields.Char(
        "Enterprise JS API Ticket",
        config_parameter="wxwork.corp_jsapi_ticket",
    )

    agent_jsapi_ticket = fields.Char(
        "Application JS API Ticket",
        config_parameter="wxwork.agent_jsapi_ticket",
    )

    ticket_interval_time = fields.Integer(
        "Pull interval time",
        config_parameter="wxwork.ticket_interval_time",
        default=1,
    )
    ticket_interval_type = fields.Selection(
        [("minutes", "Minutes"), ("hours", "Hours")],
        string="Pull Interval Unit",
        default="hours",
        config_parameter="wxwork.ticket_interval_type",
    )

    get_ticket_last_time = fields.Char(
        "Last time to get the ticket",
        config_parameter="wxwork.get_ticket_last_time",
    )

    def set_cron_ticket_interval_time(self):
        pass

    def get_jsapi_ticket(self):
        ir_config = self.env["ir.config_parameter"].sudo()
        corpid = ir_config.get_param("wxwork.corpid")
        auth_secret = ir_config.get_param("wxwork.auth_secret")
        last_time = ir_config.get_param("wxwork.get_ticket_last_time")
        interval_time = ir_config.get_param("wxwork.ticket_interval_time")
        interval_type = ir_config.get_param("wxwork.ticket_interval_type")

        if corpid == False:
            raise UserError(_("Please fill in correctly Enterprise ID."))
        elif auth_secret == False:
            raise UserError(
                _("Please fill in the application 'secret' correctly."))

        else:
            if not last_time:
                self.get_corp_ticket()
                self.get_agent_ticket()
            else:
                self.compare_time(
                    last_time, datetime.datetime.now(), interval_time, interval_type
                )

    def get_corp_ticket(self):
        ir_config = self.env["ir.config_parameter"].sudo()
        corpid = ir_config.get_param("wxwork.corpid")
        auth_secret = ir_config.get_param("wxwork.auth_secret")

        api = CorpApi(corpid, auth_secret)
        try:
            response = api.httpCall(
                CORP_API_TYPE["GET_JSAPI_TICKET"],
                {
                    "access_token": api.getAccessToken(),
                },
            )
            if self.corp_jsapi_ticket != response["ticket"]:
                ir_config.set_param(
                    "wxwork.corp_jsapi_ticket", response["ticket"]
                )
            else:
                pass

        except ApiException as ex:
            raise UserError(
                _("Error code: %s \nError description: %s \nError Details:\n%s")
                % (str(ex.errCode), Errcode.getErrcode(ex.errCode), ex.errMsg)
            )

    def get_agent_ticket(self):
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
            if self.agent_jsapi_ticket != response["ticket"]:
                ir_config.set_param(
                    "wxwork.agent_jsapi_ticket", response["ticket"]
                )
                ir_config.set_param(
                    "wxwork.get_ticket_last_time", datetime.datetime.now()
                )
            else:
                pass

        except ApiException as ex:
            raise UserError(
                _("Error code: %s \nError description: %s \nError Details:\n%s")
                % (str(ex.errCode), Errcode.getErrcode(ex.errCode), ex.errMsg)
            )

    def compare_time(self, old, new, interval_time, interval_type):
        # 字符转时间格式
        # oldTime = datetime.datetime.strptime(old, "%Y-%m-%d %H:%M:%S.%f")
        # 字符串转换为时间数组
        # oldTimeArray = time.strptime(old, "%Y-%m-%d %H:%M:%S.%f")
        # newTimeArray = time.strptime(str(new), "%Y-%m-%d %H:%M:%S.%f")
        # 转换为时间戳
        # oldTimeStamp = time.mktime(oldTimeArray)
        # newTimeStamp = time.mktime(newTimeArray)

        oldTime = datetime.datetime.strptime(old, "%Y-%m-%d %H:%M:%S.%f")
        newTime = new
        difference = (newTime - oldTime).seconds

        interval = 0
        if interval_type:
            if interval_type == "hours":
                interval = int(interval_time) * 3600
            elif interval_type == "minutes":
                interval = int(interval_time) * 60

        if int(difference) > interval:
            # 差异值超过间隔时间
            self.get_corp_ticket()
            self.get_agent_ticket()

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

                if response["errcode"] == 0:
                    if self.agent_jsapi_ticket != response["ticket"]:
                        ir_config.set_param(
                            "wxwork.agent_jsapi_ticket", response["ticket"]
                        )

                        return {
                            "type": "ir.actions.client",
                            "tag": "dialog",
                            "params": {
                                "title": _("Successful operation"),
                                "$content": _(
                                    "<div>Successfully pull the enterprise WeChat application ticket regularly.</div>"
                                ),
                                "size": "medium",
                                "reload": "true",
                            },
                        }

                    else:
                        return {
                            "type": "ir.actions.client",
                            "tag": "dialog",
                            "params": {
                                "title": _("Successful operation"),
                                "$content": _(
                                    "<div>The enterprise WeChat application ticket is within the validity period and does not need to be pulled.</div>"
                                ),
                                "size": "medium",
                            },
                        }
            except ApiException as ex:
                raise UserError(
                    _("Error code: %s \nError description: %s \nError Details:\n%s")
                    % (str(ex.errCode), Errcode.getErrcode(ex.errCode), ex.errMsg)
                )

    def cron_pull_ticket(self):
        pass

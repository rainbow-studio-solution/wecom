# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.wxwork_api.api.corp_api import CorpApi, CORP_API_TYPE
from odoo.addons.wxwork_api.api.abstract_api import ApiException
from odoo.addons.wxwork_api.api.error_code import Errcode

from datetime import datetime
import datetime

_logger = logging.getLogger(__name__)


class Company(models.Model):
    _inherit = "res.company"

    corp_jsapi_ticket = fields.Char("Enterprise JS API Ticket",)

    agent_jsapi_ticket = fields.Char("Application JS API Ticket",)

    jsapi_debug = fields.Boolean("JS API Debug mode", default=False,)

    js_api_list = fields.Char("JS API Inertface List")

    ticket_interval_time = fields.Integer("Pull interval time", default=1,)

    ticket_interval_type = fields.Selection(
        [("minutes", "Minutes"), ("hours", "Hours")],
        string="Pull Interval Unit",
        default="hours",
    )

    get_ticket_last_time = fields.Char("Last time to get the ticket",)

    def get_jsapi_ticket(self):
        """
        获取企业和应用 jsapi ticket
        """
        ir_config = self.env["ir.config_parameter"].sudo()
        debug = ir_config.get_param("wxwork.debug_enabled")
        if debug:
            _logger.info(_("Start to pull enterprise WeChat Ticket"))
        if self.corpid == False:
            raise UserError(_("Please fill in correctly Enterprise ID."))
        elif self.auth_secret == False:
            raise UserError(_("Please fill in the application 'secret' correctly."))
        else:
            if not self.get_ticket_last_time:
                self.get_corp_ticket()
                self.get_agent_ticket()
            else:
                self.compare_wxwork_ticket_time(
                    self.get_ticket_last_time,
                    datetime.datetime.now(),
                    self.ticket_interval_time,
                    self.ticket_interval_type,
                )
        if debug:
            _logger.info(_("End of pulling enterprise WeChat Ticket"))

    def get_corp_ticket(self):
        """
        拉取 企业 jsapi ticket
        """
        ir_config = self.env["ir.config_parameter"].sudo()
        debug = ir_config.get_param("wxwork.debug_enabled")
        if debug:
            _logger.info(
                _("Start to pull enterprise WeChat Ticket : Enterprise ticket")
            )
        wxapi = CorpApi(self.corpid, self.auth_secret)
        try:
            response = wxapi.httpCall(
                CORP_API_TYPE["GET_JSAPI_TICKET"],
                {"access_token": wxapi.getAccessToken(),},
            )
            if self.corp_jsapi_ticket != response["ticket"]:
                self.corp_jsapi_ticket = response["ticket"]

            if debug:
                _logger.info(
                    _("Finish pulling enterprise WeChat Ticket : Enterprise ticket")
                )
        except ApiException as ex:
            if debug:
                _logger.warning(
                    _(
                        "Failed to pull enterprise WeChat Ticket : Enterprise ticket, Error code:%s, Error info:%s"
                    )
                    % (str(ex.errCode), Errcode.getErrcode(ex.errCode), ex.errMsg)
                )
            raise UserError(
                _("Error code: %s \nError description: %s \nError Details:\n%s")
                % (str(ex.errCode), Errcode.getErrcode(ex.errCode), ex.errMsg)
            )

    def get_agent_ticket(self):
        """
        拉取 应用 jsapi ticket
        """
        ir_config = self.env["ir.config_parameter"].sudo()
        debug = ir_config.get_param("wxwork.debug_enabled")
        if debug:
            _logger.info(
                _("Start to pull enterprise WeChat Ticket : Application ticket")
            )
        wxapi = CorpApi(self.corpid, self.auth_secret)
        try:
            response = wxapi.httpCall(
                CORP_API_TYPE["GET_TICKET"],
                {"access_token": wxapi.getAccessToken(), "type": "agent_config",},
            )
            if self.agent_jsapi_ticket != response["ticket"]:
                self.agent_jsapi_ticket = response["ticket"]
                self.get_ticket_last_time = datetime.datetime.now()

            if debug:
                _logger.info(
                    _("Finish pulling enterprise WeChat Ticket : Application ticket")
                )
        except ApiException as ex:
            if debug:
                _logger.warning(
                    _(
                        "Failed to pull enterprise WeChat Ticket : Application ticket, Error code:%s, Error info:%s"
                    )
                    % (str(ex.errCode), Errcode.getErrcode(ex.errCode), ex.errMsg)
                )
            raise UserError(
                _("Error code: %s \nError description: %s \nError Details:\n%s")
                % (str(ex.errCode), Errcode.getErrcode(ex.errCode), ex.errMsg)
            )

    def compare_wxwork_ticket_time(self, old, new, interval_time, interval_type):
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

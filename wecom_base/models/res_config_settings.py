# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from random import weibullvariate
from odoo import models, fields, api, _
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException # type: ignore

import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # 基础
    is_wecom_organization = fields.Boolean(
        related="company_id.is_wecom_organization", readonly=False
    )
    company_name = fields.Char(
        related="company_id.name", string="Company Name", readonly=False
    )
    abbreviated_name = fields.Char(
        related="company_id.abbreviated_name", readonly=False
    )
    corpid = fields.Char(string="Corp ID", related="company_id.corpid", readonly=False)

    wecom_jsapi_ticket = fields.Char(
        string="JSAPI Ticket", related="company_id.wecom_jsapi_ticket", readonly=False
    )
    wecom_jsapi_ticket_expiration_time = fields.Datetime(
        string="Expiration time of JSAPI Ticket",
        related="company_id.wecom_jsapi_ticket_expiration_time",
        readonly=False,
    )

    debug_enabled = fields.Boolean("Turn on debug mode", default=True)

    resources_path = fields.Char(
        "WeCom resources storage path",
        config_parameter="wecom.resources_path",
    )

    global_error_code_url = fields.Char(
        "Global error code page URL",
        config_parameter="wecom.global_error_code_url",
    )

    global_error_code_item_selection_code = fields.Char(
        "Global error code item selection code",
        config_parameter="wecom.global_error_code_item_selection_code",
    )  # 错误码排查方法的选取属性。

    module_rainbow_community_theme = fields.Boolean("Rainbow Community Theme")
    module_wecom_contacts = fields.Boolean("WeCom Contacts")
    module_wecom_contacts_sync = fields.Boolean("WeCom Contacts Synchronized")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values() # type: ignore
        ir_config = self.env["ir.config_parameter"].sudo()

        debug_enabled = (
            True if ir_config.get_param("wecom.debug_enabled") == "True" else False
        )

        res.update(
            debug_enabled=debug_enabled,
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values() # type: ignore
        ir_config = self.env["ir.config_parameter"].sudo()
        ir_config.set_param("wecom.debug_enabled", self.debug_enabled or "False")

    def open_wecom_company(self):
        return {
            "type": "ir.actions.act_window",
            "name": "My Company",
            "view_mode": "form",
            "res_model": "res.company",
            "res_id": self.env.company.id,
            "target": "current",
            "context": {
                "form_view_initial_mode": "edit",
            },
        }

    @api.depends("company_id")
    def _compute_wecom_company_corpid(self):
        company_corpid = self.company_id.corpid if self.company_id.corpid else ""  # type: ignore

        for record in self:
            record.wecom_company_corpid = company_corpid    # type: ignore

    @api.model
    def open_wecom_settings(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "wecom_base.res_config_settings_view_form"
        )
        action["target"] = "new"

        return action

    def get_app_info(self):
        """
        获取企业应用信息
        :param agentid:
        :return:
        """

    def get_corp_jsapi_ticket(self):
        """
        获取企业的jsapi_ticket
        :return:
        """
        ir_config = self.env["ir.config_parameter"].sudo()
        debug = ir_config.get_param("wecom.debug_enabled")
        if debug:
            _logger.info(
                _("Start getting ticket for company [%s]") % (self.company_id.name) # type: ignore
            )
        try:
            if (
                self.wecom_jsapi_ticket_expiration_time
                and self.wecom_jsapi_ticket_expiration_time > datetime.now()
            ):
                # 未过期，
                # print("未过期")
                msg = {
                    "title": _("Tips"),
                    "message": _("Ticket is still valid, and no update is required!"),
                    "sticky": False,
                }
                return self.env["wecomapi.tools.action"].WecomInfoNotification(msg)
            else:
                # print("过期")
                wecom_api = self.env["wecom.service_api"].InitServiceApi(self.company_id.corpid, self.contacts_app_id.secret) # type: ignore
                response = wecom_api.httpCall(
                    self.env["wecom.service_api_list"].get_server_api_call(
                        "GET_JSAPI_TICKET"
                    ),
                    {},
                )
                # print(response)
        except ApiException as ex:
            return self.env["wecomapi.tools.action"].ApiExceptionDialog(
                ex, raise_exception=True
            )
        else:
            if response["errcode"] == 0:
                self.write(
                    {
                        "wecom_jsapi_ticket": response["ticket"],
                        "wecom_jsapi_ticket_expiration_time": datetime.now()
                        + timedelta(seconds=response["expires_in"]),
                    }
                )
                msg = {
                    "title": _("Tips"),
                    "message": _("Successfully obtained ticket!"),
                    "sticky": False,
                    "next": {
                        "type": "ir.actions.client",
                        "tag": "reload",
                    },
                }
                return self.env["wecomapi.tools.action"].WecomSuccessNotification(msg)

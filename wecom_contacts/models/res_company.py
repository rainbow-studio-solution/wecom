# -*- coding: utf-8 -*-

from ast import literal_eval
from collections import defaultdict

from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
from odoo.http import request
from odoo import api, fields, models, tools, _
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException   # type: ignore
import logging

_logger = logging.getLogger(__name__)


class Company(models.Model):
    _inherit = "res.company"

    # 通讯录
    contacts_app_id = fields.Many2one(
        "wecom.apps",
        string="Contacts Application",
        # required=True,
        # default=lambda self: self.env.company,
        domain="[('company_id', '=', current_company_id)]",
    )

    wecom_contacts_join_qrcode_enabled = fields.Boolean(
        string="Enable to join the enterprise QR code",
        default=True,
        copy=False,
    )
    wecom_contacts_join_qrcode = fields.Char(
        string="Join enterprise wechat QR code",
        copy=False,
        readonly=True,
    )
    wecom_contacts_join_qrcode_size_type = fields.Selection(
        [
            ("1", "171px x 171px"),
            ("2", "399px x 399px"),
            ("3", "741px x 741px"),
            ("4", "2052px x 2052px"),
        ],
        string="Join enterprise wechat QR code  size type",
        default="2",
        required=True,
    )
    wecom_contacts_join_qrcode_last_time = fields.Datetime(
        string="Get the last time of QR code (UTC)",
        copy=False,
    )

    def cron_get_corp_jsapi_ticket(self):
        """
        定时任务，每隔两小时更新企业的jsapi_ticket
        """
        for company in self:
            if ( company.is_wecom_organization and company.corpid and company.contacts_app_id): # type: ignore
                _logger.info(
                    _("Automatic tasks:Start getting JSAPI ticket for company [%s]")
                    % (company.name)    # type: ignore
                )
                if (
                    company.wecom_jsapi_ticket_expiration_time  # type: ignore
                    and company.wecom_jsapi_ticket_expiration_time > datetime.now() # type: ignore
                ):
                    _logger.info(
                        _(
                            "The company [%s] ticket is still valid and does not need to be updated!"
                        )
                        % (company.name)    # type: ignore
                    )
                else:
                    try:
                        wecom_api = self.env["wecom.service_api"].InitServiceApi(
                            self.company_id.corpid, self.contacts_app_id.secret # type: ignore
                        )
                        response = wecom_api.httpCall(
                            self.env["wecom.service_api_list"].get_server_api_call(
                                "GET_JSAPI_TICKET"
                            ),
                            {},
                        )
                    except ApiException as ex:
                        _logger.error(
                            _("Error in obtaining company [%s] ticket, reason: %s")
                            % (company.name, ex)    # type: ignore
                        )
                    else:
                        if response["errcode"] == 0:
                            company.write(
                                {
                                    "wecom_jsapi_ticket": response["ticket"],
                                    "wecom_jsapi_ticket_expiration_time": datetime.now()
                                    + timedelta(seconds=response["expires_in"]),
                                }
                            )
                    finally:
                        _logger.info(
                            _("Automatic tasks:End of company [%s] JSAPI ticket update")
                            % (company.name)    # type: ignore
                        )

    # TODO: 使用任务 获取IP

    # def cron_get_wecom_api_domain_ip(self):
    def get_wecom_api_domain_ip(self):
        """
        获取企业微信API域名IP段
        """
        ir_config = self.env["ir.config_parameter"].sudo()
        debug = ir_config.get_param("wecom.debug_enabled")
        companies = self.search([])

        for company in companies: # type: ignore
            if not company.contacts_app_id: # type: ignore
                raise ValidationError(_("Please bind contact app!"))

            if debug:
                _logger.info(_("Start to get enterprise wechat API domain name IP segment"))
            try:
                wecomapi = self.env["wecom.service_api"].InitServiceApi(company.corpid, company.contacts_app_id.secret) # type: ignore

                response = wecomapi.httpCall(
                    self.env["wecom.service_api_list"].get_server_api_call(
                        "GET_API_DOMAIN_IP"
                    ),
                    {},
                )
                if response["errcode"] == 0:
                    self.env["ir.config_parameter"].set_param(
                        "wecom.api_domain_ip", response["ip_list"]
                    )
                    return {"type": "ir.actions.client", "tag": "reload"}  # 刷新页面

            except ApiException as ex:
                return self.env["wecomapi.tools.action"].ApiExceptionDialog(
                    ex, raise_exception=True
                )

            finally:
                if debug:
                    _logger.info(
                        _("End obtaining enterprise wechat API domain name IP segment")
                    )

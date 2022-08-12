# -*- coding: utf-8 -*-

import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import time

from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException

import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )

    wecom_api_domain_ip = fields.Char(
        "Wecom API Domain IP", config_parameter="wecom.api_domain_ip",
    )

    # 加入企微微信二维码
    contacts_join_qrcode_enabled = fields.Boolean(
        related="company_id.wecom_contacts_join_qrcode_enabled", readonly=False
    )
    contacts_join_qrcode = fields.Char(
        related="company_id.wecom_contacts_join_qrcode", readonly=False
    )
    contacts_join_qrcode_size_type = fields.Selection(
        related="company_id.wecom_contacts_join_qrcode_size_type", readonly=False
    )
    contacts_join_qrcode_last_time = fields.Datetime(
        related="company_id.wecom_contacts_join_qrcode_last_time", readonly=False
    )

    # 通讯录
    contacts_app_id = fields.Many2one(
        related="company_id.contacts_app_id", readonly=False
    )

    contacts_secret = fields.Char(related="contacts_app_id.secret", readonly=False)

    # contacts_access_token = fields.Char(related="contacts_app_id.access_token")

    contacts_app_config_ids = fields.One2many(
        related="contacts_app_id.app_config_ids", readonly=False,
    )

    contacts_app_callback_service_ids = fields.One2many(
        related="contacts_app_id.app_callback_service_ids", readonly=False
    )

    module_wecom_contacts_sync = fields.Boolean("WeCom Contacts Synchronized")

    module_wecom_material = fields.Boolean("WeCom Material")
    module_wecom_auth_oauth = fields.Boolean("WeCom Authentication")
    module_wecom_message = fields.Boolean("WeCom Message")
    module_portal = fields.Boolean("Customer Portal")
    module_wecom_portal = fields.Boolean("Wecom Portal")
    module_wecom_msgaudit = fields.Boolean("Wecom Session Content Archive")
    module_wecom_attendance = fields.Boolean("WeCom Attendances")
    module_wecom_approval = fields.Boolean("WeCom Approvals")

    def cron_get_join_qrcode(self):
        """
        自动任务获取加入企业二维码
        """
        companies = self.env["res.company"].search(
            [
                ("is_wecom_organization", "=", True),
                ("wecom_contacts_join_qrcode_enabled", "=", True),
            ]
        )
        for company in companies:
            _logger.info(
                _("Automatic task:Start to get join enterprise QR code of company [%s]")
                % (company.name)
            )
            if not company.contacts_app_id:
                _logger.info(
                    _("Automatic task:Please bind the contact app of company [%s]!")
                    % (company.name)
                )
            elif not company.wecom_contacts_join_qrcode_enabled:
                _logger.info(
                    _(
                        "Automatic task:Please enable the company [%s] to join the enterprise wechat QR code function!"
                    )
                    % (company.name)
                )
            else:
                try:
                    wecomapi = self.env["wecom.service_api"].InitServiceApi(
                        company.corpid, company.contacts_app_id.secret
                    )

                    last_time = company.wecom_contacts_join_qrcode_last_time
                    size_type = company.wecom_contacts_join_qrcode_size_type
                    # 超期
                    overdue = False
                    if last_time:
                        overdue = self.env[
                            "wecomapi.tools.datetime"
                        ].cheeck_days_overdue(last_time, 7)
                    if not last_time or overdue:
                        response = wecomapi.httpCall(
                            self.env["wecom.service_api_list"].get_server_api_call(
                                "GET_JOIN_QRCODE"
                            ),
                            {"size_type": size_type},
                        )
                        if response["errcode"] == 0:
                            company.write(
                                {
                                    "wecom_contacts_join_qrcode": response[
                                        "join_qrcode"
                                    ],
                                    "wecom_contacts_join_qrcode_last_time": datetime.datetime.now(),
                                }
                            )
                except ApiException as ex:
                    error = self.env["wecom.service_api_error"].get_error_by_code(
                        ex.errCode
                    )
                    _logger.warning(
                        _(
                            "Automatic task:Error in obtaining the QR code of joining company [%s],error code: %s, error name: %s, error message: %s"
                        )
                        % (company.name, str(ex.errCode), error["name"], ex.errMsg)
                    )
            _logger.info(
                _(
                    "Automatic task:End obtaining joining enterprise QR code of company [%s]"
                )
                % (company.name)
            )

    def get_join_qrcode(self):
        """
        获取加入企业二维码
        """
        # self.contacts_app_id.get_join_qrcode()
        ir_config = self.env["ir.config_parameter"].sudo()
        debug = ir_config.get_param("wecom.debug_enabled")

        if not self.contacts_app_id:
            raise ValidationError(_("Please bind contact app!"))

        if not self.contacts_join_qrcode_enabled:
            raise ValidationError(
                _("Please enable the function of join enterprise QR code!")
            )

        if debug:
            _logger.info(
                _("Start getting join enterprise QR code of company [%s]")
                % (self.company_id.name)
            )
        try:
            wecomapi = self.env["wecom.service_api"].InitServiceApi(
                self.company_id.corpid, self.contacts_app_id.secret
            )

            last_time = self.contacts_join_qrcode_last_time
            size_type = self.contacts_join_qrcode_size_type
            # 超期
            overdue = False
            if last_time:
                overdue = self.env["wecomapi.tools.datetime"].cheeck_days_overdue(
                    last_time, 7
                )
            if not last_time or overdue:
                response = wecomapi.httpCall(
                    self.env["wecom.service_api_list"].get_server_api_call(
                        "GET_JOIN_QRCODE"
                    ),
                    {"size_type": size_type},
                )
                if response["errcode"] == 0:
                    self.company_id.write(
                        {
                            "wecom_contacts_join_qrcode": response["join_qrcode"],
                            "wecom_contacts_join_qrcode_last_time": datetime.datetime.now(),
                        }
                    )
                    # self.contacts_join_qrcode=response["join_qrcode"]
                    # self.contacts_join_qrcode_last_time =  datetime.datetime.now()

        except ApiException as ex:
            return self.env["wecomapi.tools.action"].ApiExceptionDialog(
                ex, raise_exception=True
            )

        finally:
            if debug:
                _logger.info(
                    _("End getting join enterprise QR code of company [%s]")
                    % (self.company_id.name)
                )

    # TODO: 使用任务 获取IP

    def get_wecom_api_domain_ip(self):
        """
        获取企业微信API域名IP段
        """
        ir_config = self.env["ir.config_parameter"].sudo()
        debug = ir_config.get_param("wecom.debug_enabled")

        if not self.contacts_app_id:
            raise ValidationError(_("Please bind contact app!"))

        if debug:
            _logger.info(_("Start to get enterprise wechat API domain name IP segment"))
        try:
            wecomapi = self.env["wecom.service_api"].InitServiceApi(
                self.company_id.corpid, self.contacts_app_id.secret
            )

            response = wecomapi.httpCall(
                self.env["wecom.service_api_list"].get_server_api_call(
                    "GET_API_DOMAIN_IP"
                ),
                {},
            )
            if response["errcode"] == 0:
                ir_config.sudo().set_param("wecom.api_domain_ip", response["ip_list"])

        except ApiException as ex:
            return self.env["wecomapi.tools.action"].ApiExceptionDialog(
                ex, raise_exception=True
            )

        finally:
            if debug:
                _logger.info(
                    _("End obtaining enterprise wechat API domain name IP segment")
                )


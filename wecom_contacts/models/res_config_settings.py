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

    # 加入企微微信二维码
    contacts_join_qrcode_enabled = fields.Boolean(related="company_id.wecom_contacts_join_qrcode_enabled", readonly=False)
    contacts_join_qrcode  = fields.Char(related="company_id.wecom_contacts_join_qrcode", readonly=False)
    contacts_join_qrcode_size_type  = fields.Selection(related="company_id.wecom_contacts_join_qrcode_size_type", readonly=False)
    contacts_join_qrcode_last_time  = fields.Datetime(related="company_id.wecom_contacts_join_qrcode_last_time", readonly=False)


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
    module_wecom_hrm = fields.Boolean("WeCom HRM")
    module_wecom_material = fields.Boolean("WeCom Material")
    module_wecom_auth_oauth = fields.Boolean("WeCom Authentication")
    module_wecom_message = fields.Boolean("WeCom Message")


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
            raise ValidationError(_("Please enable the function of join enterprise QR code!"))

        if debug:
            _logger.info(
                _("Start getting join enterprise QR code for app [%s] of company [%s]")
                % (self.contacts_app_id.name, self.company_id.name)
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
                    self.company_id.write({
                        'wecom_contacts_join_qrcode':response["join_qrcode"], 
                        'wecom_contacts_join_qrcode_last_time':datetime.datetime.now(), 
                        })
                    # self.contacts_join_qrcode=response["join_qrcode"]
                    # self.contacts_join_qrcode_last_time =  datetime.datetime.now()


            
        except ApiException as ex:
            return self.env["wecomapi.tools.action"].ApiExceptionDialog(
                ex, raise_exception=True
            )


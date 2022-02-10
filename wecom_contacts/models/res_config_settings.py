# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

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

    # 通讯录
    contacts_app_id = fields.Many2one(
        related="company_id.contacts_app_id", readonly=False
    )

    contacts_secret = fields.Char(related="contacts_app_id.secret", readonly=False)

    # contacts_access_token = fields.Char(related="contacts_app_id.access_token")

    contacts_app_config_ids = fields.One2many(
        # related="company_id.contacts_auto_sync_hr_enabled", readonly=False
        related="contacts_app_id.app_config_ids",
        # domain="[('company_id', '=', company_id),('app_id', '=', contacts_app_id)]",
        readonly=False,
    )

    contacts_app_callback_service_ids = fields.One2many(
        related="contacts_app_id.app_callback_service_ids", readonly=False
    )

    module_wecom_contacts_sync= fields.Boolean("WeCom Contacts Synchronized")
    module_wecom_hrm= fields.Boolean("WeCom HRM")
    module_wecom_material= fields.Boolean("WeCom Material")
    module_wecom_message= fields.Boolean("WeCom Message")
    

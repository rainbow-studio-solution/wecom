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

    def generate_service(self):
        """
        生成服务
        :return:
        """
        code = self.env.context.get("code")
        if bool(code) and code == "contacts":
            for record in self:
                if not record.contacts_app_id:
                    raise ValidationError(_("Please bind contact app!"))
                else:
                    record.contacts_app_id.with_context(code=code).generate_service()
        # super(ResConfigSettings, self).generate_service()

    def generate_parameters(self):
        """
        生成参数
        :return:
        """
        code = self.env.context.get("code")
        if bool(code) and code == "contacts":
            for record in self:
                if not record.contacts_app_id:
                    raise ValidationError(_("Please bind contact app!"))
                else:
                    record.contacts_app_id.with_context(code=code).generate_parameters()
        # super(ResConfigSettings, self).generate_parameters()

    def get_join_qrcode(self):
        """
        获取加入企业二维码
        """
        self.contacts_app_id.get_join_qrcode()

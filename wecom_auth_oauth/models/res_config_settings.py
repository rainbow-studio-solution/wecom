# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException


import werkzeug.urls
import werkzeug.utils
import urllib
import datetime
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

    auth_app_id = fields.Many2one(related="company_id.auth_app_id", readonly=False,)
    auth_agentid = fields.Integer(related="auth_app_id.agentid", readonly=False)
    auth_secret = fields.Char(related="auth_app_id.secret", readonly=False)

    auth_app_config_ids = fields.One2many(
        # related="company_id.contacts_auto_sync_hr_enabled", readonly=False
        related="auth_app_id.app_config_ids",
        # domain="[('company_id', '=', company_id),('app_id', '=', contacts_app_id)]",
        readonly=False,
    )

    def set_oauth_provider_wecom(self):
        self.auth_app_id.set_oauth_provider_wecom()

    def generate_parameters(self):
        """
        生成参数
        :return:
        """
        code = self.env.context.get("code")
        if bool(code) and code == "auth":
            for record in self:
                # if not record.contacts_app_id:
                #     raise ValidationError(_("Please bind contact app!"))
                # else:
                record.auth_app_id.with_context(code=code).generate_parameters()
        super(ResConfigSettings, self).generate_parameters()

    def get_app_info(self):
        """
        获取应用信息
        :return:
        """
        app = self.env.context.get("app")
        for record in self:
            if app == "auth" and (
                record.auth_app_id.agentid == 0 or record.auth_app_id.secret == ""
            ):
                raise UserError(_("Auth application ID and secret cannot be empty!"))
            else:
                record.auth_app_id.get_app_info()
        super(ResConfigSettings, self).get_app_info()

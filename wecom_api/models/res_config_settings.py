from random import weibullvariate
from odoo import models, fields, api, _


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

    contacts_app_config_ids = fields.One2many(
        # related="company_id.contacts_auto_sync_hr_enabled", readonly=False
        related="contacts_app_id.app_config_ids",
        # domain="[('company_id', '=', company_id),('app_id', '=', contacts_app_id)]",
        readonly=False,
    )

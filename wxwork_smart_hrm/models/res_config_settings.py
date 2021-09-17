# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )

    contacts_secret = fields.Char(related="company_id.contacts_secret", readonly=False)

    contacts_access_token = fields.Char(related="company_id.contacts_access_token")

    contacts_auto_sync_hr_enabled = fields.Boolean(
        related="company_id.contacts_auto_sync_hr_enabled", readonly=False
    )

    contacts_sync_hr_department_id = fields.Integer(
        related="company_id.contacts_sync_hr_department_id", readonly=False
    )

    contacts_edit_enabled = fields.Boolean(
        related="company_id.contacts_edit_enabled", readonly=False
    )

    contacts_sync_user_enabled = fields.Boolean(
        related="company_id.contacts_sync_user_enabled", readonly=False
    )

    contacts_use_system_default_avatar = fields.Boolean(
        related="company_id.contacts_use_system_default_avatar", readonly=False
    )

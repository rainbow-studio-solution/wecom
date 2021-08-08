# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class Company(models.Model):
    _inherit = "res.company"

    contacts_secret = fields.Char(
        "Contact Secret", default="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    )
    contacts_access_token = fields.Char(string="Contact token", readonly=True,)
    contacts_auto_sync_hr_enabled = fields.Boolean(
        "Allow Enterprise WeChat Contacts are automatically updated to HR",
        default=True,
    )
    contacts_sync_hr_department_id = fields.Integer(
        "Enterprise WeChat department ID to be synchronized", default=1,
    )
    contacts_edit_enabled = fields.Boolean(
        "Allow API to edit Enterprise WeChat contacts",
        default=False,
        # readonly=True,
    )
    contacts_sync_user_enabled = fields.Boolean(
        "Allow Enterprise WeChat contacts to automatically update system accounts",
        default=False,
    )
    contacts_sync_avatar_enabled = fields.Boolean("Sync Avatar", default=False,)
    contacts_always_update_avatar_enabled = fields.Boolean(
        "Always update avatar", default=False,
    )

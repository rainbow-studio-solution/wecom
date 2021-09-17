# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.modules.module import get_module_resource


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
    contacts_use_system_default_avatar = fields.Boolean(
        "Use system default Avatar", default=True,
    )

    @api.onchange("contacts_use_system_default_avatar")
    def _onchange_contacts_use_system_default_avatar(self):
        employees = self.env["hr.employee"].search(
            [
                ("is_wxwork_employee", "=", True),
                "|",
                ("active", "=", True),
                ("active", "=", False),
            ]
        )
        for employee in employees:
            employee.write(
                {"use_system_avatar": self.contacts_use_system_default_avatar}
            )

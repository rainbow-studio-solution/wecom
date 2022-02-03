# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.modules.module import get_module_resource


class Company(models.Model):
    _inherit = "res.company"

    # @api.onchange("contacts_use_system_default_avatar")
    # def _onchange_contacts_use_system_default_avatar(self):
    #     employees = self.env["hr.employee"].search(
    #         [
    #             ("is_wecom_user", "=", True),
    #             "|",
    #             ("active", "=", True),
    #             ("active", "=", False),
    #         ]
    #     )
    #     for employee in employees:
    #         employee.write(
    #             {"use_system_avatar": self.contacts_use_system_default_avatar}
    #         )

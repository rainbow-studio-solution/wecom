# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.modules.module import get_module_resource


class Company(models.Model):
    _inherit = "res.company"

    attendance_app_id = fields.Many2one(
        "wecom.apps",
        string="Attendance Application",
        domain="[('company_id', '=', current_company_id)]",
    )

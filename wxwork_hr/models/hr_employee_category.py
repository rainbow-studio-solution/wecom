# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class EmployeeCategory(models.Model):
    _inherit = "hr.employee.category"

    tagid = fields.Integer(string="Enterprise WeChat Tag ID", readonly=True,)
    is_wxwork_category = fields.Boolean(string="Enterprise WeChat Tag", default=False,)


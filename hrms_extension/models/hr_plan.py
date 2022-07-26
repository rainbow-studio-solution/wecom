# -*- coding: utf-8 -*-

from odoo import api, fields, models


class HrPlan(models.Model):
    _inherit = "hr.plan"

    name = fields.Char("Name", required=True, translate=True)

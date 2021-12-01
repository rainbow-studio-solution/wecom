# -*- coding: utf-8 -*-

from odoo import api, fields, models


# class HrPlanActivityType(models.Model):
#     _inherit = "hr.plan.activity.type"

#     responsible = fields.Selection(
#         [
#             ("coach", "Coach"),
#             ("manager", "Manager"),
#             ("employee", "Employee"),
#             ("other", "Other"),
#         ],
#         default="employee",
#         string="Responsible",
#         required=True,
#         translate=True,
#     )


class HrPlan(models.Model):
    _inherit = "hr.plan"

    name = fields.Char("Name", required=True, translate=True)

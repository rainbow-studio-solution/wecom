# -*- coding: utf-8 -*-

from odoo import api, fields, models


class HrPlan(models.Model):
    _inherit = "hr.plan"

    name = fields.Char("Name", required=True, translate=True)


class HrPlanActivityType(models.Model):
    _inherit = "hr.plan.activity.type"

    summary = fields.Char(
        "Summary",
        compute="_compute_default_summary",
        store=True,
        readonly=False,
        translate=True,
    )  # 摘要

    responsible = fields.Selection(
        [
            ("coach", "Coach"),
            ("manager", "Manager"),
            ("employee", "Employee"),
            ("other", "Other"),
        ],
        default="employee",
        string="Responsible",
        required=True,
        translate=True,
    )  # 负责人


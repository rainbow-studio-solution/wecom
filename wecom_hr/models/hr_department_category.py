# -*- coding: utf-8 -*-

from random import randint
from odoo import api, fields, models, _


class DepartmentCategory(models.Model):
    _name = "hr.department.category"
    _description = "Department Category"

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char(string="Tag Name", required=True)
    color = fields.Integer(string="Color Index", default=_get_default_color)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        index=True,
        default=lambda self: self.env.company,
    )
    department_ids = fields.Many2many(
        "hr.department",
        "department_category_rel",
        "category_id",
        "dmp_id",
        string="Departments",
    )
    tagid = fields.Integer(
        string="WeCom Tag ID",
        readonly=True,
        default=0,
        help="Tag ID, non negative integer. When this parameter is specified, the new tag will generate the corresponding tag ID. if it is not specified, it will be automatically increased by the current maximum ID.",
    )
    is_wecom_category = fields.Boolean(
        string="WeCom Tag",
        default=False,
    )

    _sql_constraints = [
        ("name_uniq", "unique (name)", "Tag name already exists !"),
    ]

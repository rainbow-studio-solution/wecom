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
        string="Enterprise WeChat Tag ID",
        readonly=True,
        default=0,
        help="标签id，非负整型，指定此参数时新增的标签会生成对应的标签id，不指定时则以目前最大的id自增。",
    )
    is_wxwork_category = fields.Boolean(string="Enterprise WeChat Tag", default=False,)

    _sql_constraints = [
        ("name_uniq", "unique (name)", "Tag name already exists !"),
    ]


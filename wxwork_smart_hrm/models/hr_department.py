# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class Department(models.Model):

    _inherit = "hr.department"
    # _order = "wxwork_department_order asc,complete_name"
    # _order = "display_name"

    category_ids = fields.Many2many(
        "hr.department.category",
        "department_category_rel",
        "dmp_id",
        "category_id",
        groups="hr.group_hr_manager",
        string="Tags",
        readonly=True,
    )

    wxwork_department_id = fields.Integer(
        string="Enterprise WeChat department ID", readonly=True, default="0",
    )

    wxwork_department_parent_id = fields.Integer(
        "Enterprise WeChat parent department ID",
        help="Parent department ID,32-bit integer.Root department is 1",
        readonly=True,
    )
    wxwork_department_order = fields.Char(
        "Enterprise WeChat department sort",
        default="1",
        help="Order value in parent department. The higher order value is sorted first. The value range is[0, 2^32)",
        readonly=True,
    )
    is_wxwork_department = fields.Boolean(
        string="Enterprise WeChat Department", readonly=True, default=False,
    )


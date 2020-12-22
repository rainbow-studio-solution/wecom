# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class Employee(models.Model):
    _inherit = "hr.employee"
    _description = "Enterprise WeChat employees"
    _order = "wxwork_user_order"

    wxwork_id = fields.Char(string="Enterprise WeChat user Id", readonly=True,)

    alias = fields.Char(string="Alias", readonly=True,)

    # wxwork_department_ids = fields.Many2many(
    #     "hr.department",
    #     string="Enterprise WeChat multi-department",
    #     readonly=True,
    #
    # )

    qr_code = fields.Binary(
        string="Personal QR code",
        help="Personal QR code, Scan can be added as external contact",
        readonly=True,
    )
    wxwork_user_order = fields.Char(
        "Enterprise WeChat user sort",
        default="0",
        help="The sort value within the department, the default is 0. The quantity must be the same as the department, The greater the value the more sort front.The value range is [0, 2^32)",
        readonly=True,
    )
    is_wxwork_employee = fields.Boolean(
        string="Enterprise WeChat employees", readonly=True, default=False,
    )

    user_check_tick = fields.Boolean(string="User Check Tick", default=False,)


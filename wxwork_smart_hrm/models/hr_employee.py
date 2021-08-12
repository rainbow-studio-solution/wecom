# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class HrEmployeePrivate(models.Model):
    _inherit = "hr.employee"
    _order = "wxwork_user_order"

    category_ids = fields.Many2many(
        "hr.employee.category",
        "employee_category_rel",
        "emp_id",
        "category_id",
        groups="hr.group_hr_manager",
        string="Tags",
        domain="[('is_wxwork_category', '=',False)]",
    )

    wxwork_id = fields.Char(string="Enterprise WeChat user Id", readonly=True,)

    alias = fields.Char(string="Alias", readonly=True,)
    english_name = fields.Char(string="English Name", readonly=True,)

    department_ids = fields.Many2many(
        "hr.department", string="Multiple departments", readonly=True,
    )
    use_system_avatar = fields.Boolean(readonly=True, default=True)
    avatar = fields.Char(string="Avatar")
    # avatar = fields.Char(string="Avatar", readonly=True, img_height=95)
    qr_code = fields.Char(
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

    # TODO 待处理 增加标签成员 和 删除标签成员
    # @api.onchange("category_ids")
    # def _onchange_category_ids(self):
    #     print(self.category_ids)

    # @api.model
    # def create(self, vals):
    #     employee = super(HrEmployeePrivate, self).create(vals)

    # def write(self, vals):
    #     res = super(HrEmployeePrivate, self).write(vals)

    #     if self.is_wxwork_employee:
    #         # 检测是企业微信员工
    #         if len(self.category_ids) > 0:
    #             pass
    #         else:
    #             pass
    #     return res

    # def unlink(self):
    #     super(HrEmployeePrivate, self).unlink()

# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class HrEmployeePrivate(models.Model):
    _inherit = "hr.employee"
    _description = "Enterprise WeChat employees"
    _order = "wxwork_user_order"

    wxwork_id = fields.Char(string="Enterprise WeChat user Id", readonly=True,)

    alias = fields.Char(string="Alias", readonly=True,)

    department_ids = fields.Many2many(
        "hr.department", string="Multiple departments", readonly=True,
    )

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

    # TODO 待处理 增加标签成员 和 删除标签成员
    # @api.onchange("category_ids")
    # def _onchange_category_ids(self):
    #     print(self.category_ids)

    @api.model
    def create(self, vals):
        employee = super(HrEmployeePrivate, self).create(vals)

    def write(self, vals):
        res = super(HrEmployeePrivate, self).write(vals)

        if self.is_wxwork_employee:
            # 检测是企业微信员工
            if len(self.category_ids) > 0:
                # 选择了标签，
                print(self.category_ids)
            else:
                # 未选择了标签，
                pass
        return res

    def unlink(self):
        super(HrEmployeePrivate, self).unlink()

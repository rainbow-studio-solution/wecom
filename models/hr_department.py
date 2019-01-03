# -*- coding: utf-8 -*-

from odoo import api, fields, models

# _logger = logging.getLogger(__name__)


class HrDepartment(models.Model):
    _inherit = 'hr.department'
    _description = '企业微信部门'
    _order = 'wxwork_department_id'

    # name = fields.Char('微信部门名称',help='长度限制为1~32个字符，字符不能包括\:?”<>｜')
    wxwork_department_id = fields.Integer(
        '企微部门ID', default=0, help='企业微信部门ID', readonly=True,)
    wxwork_department_parent_id = fields.Integer(
        '企微上级部门ID', default=1, help='上级部门id,32位整型。根部门为1', readonly=True,)
    wxwork_department_order = fields.Char(
        '企微部门排序',
        default='1',
        help='在父部门中的次序值。order值大的排序靠前。值范围是[0, 2^32)',
        readonly=True,
    )
    is_wxwork_department = fields.Boolean('企微部门', readonly=True)

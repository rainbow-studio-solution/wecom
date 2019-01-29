# -*- coding: utf-8 -*-

from odoo import api, fields, models, registry, SUPERUSER_ID

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _description = '企业微信员工'
    _order = 'wxwork_user_order'

    wxwork_id = fields.Char(string='企微用户Id', readonly=True)
    alias = fields.Char(string='别名', readonly=True)
    department_ids = fields.Many2many('hr.department', string='企微多部门', readonly=True)
    qr_code = fields.Binary(string='个人二维码', help='员工个人二维码，扫描可添加为外部联系人', readonly=True)
    wxwork_user_order = fields.Char(
        '企微用户排序',
        default='0',
        help='部门内的排序值，默认为0。数量必须和department一致，数值越大排序越前面。值范围是[0, 2^32)',
        readonly=True,
    )
    is_wxwork_employee = fields.Boolean('企微员工', readonly=True)

# -*- coding: utf-8 -*-

from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _description = '企业微信员工'
    _order = 'wxwork_user_order'

    userid = fields.Char(string='企微用户Id', readonly=True)
    alias = fields.Char(string='别名')
    department_ids = fields.Many2many('hr.department', string='企微多部门')
    qr_code = fields.Binary(string='个人二维码', help='员工个人二维码，扫描可添加为外部联系人')
    wxwork_user_order = fields.Char(
        '企微用户排序',
        default='0',
        help='部门内的排序值，默认为0。数量必须和department一致，数值越大排序越前面。值范围是[0, 2^32)',
        readonly=True,
    )
    is_wxwork_user = fields.Boolean('企微用户', readonly=True)

    @api.multi
    def create_employee(self,json):
        record = self.sudo().create({
            'userid': json['userid'],
            'name': json['name'],
            # 'gender': Common(obj['gender']).gender(),
            # 'marital': not fields,  # 不生成婚姻状况
            # 'image': Common(obj['avatar']).avatar2image(),
            # 'image': self._avatar2image(obj['avatar']),
            # 'mobile_phone': obj['mobile'],
            # 'work_phone': obj['telephone'],
            # 'work_email': obj['email'],
            # 'active': obj['enable'],
            # 'alias': obj['alias'],
            # 'department_ids': [(6, 0, department_ids)],
            # 'wxwork_user_order': obj['order'],
            'is_wxwork_user': True
        })

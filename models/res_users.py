# -*- coding: utf-8 -*-

from odoo import api, fields, models

class Users(models.Model):
    _inherit = 'res.users'
    _description = '企业微信员工'
    _order = 'wxwork_user_order'

    userid = fields.Char(string='企微用户Id', readonly=True)
    is_wxwork_notice =fields.Boolean('是否接收提醒', default=True)
    wxwork_user_order = fields.Char(
        '企微用户排序',
        default='0',
        help='部门内的排序值，默认为0。数量必须和department一致，数值越大排序越前面。值范围是[0, 2^32)',
        readonly=True,
    )

    @api.multi
    def wxwork_message_send(self):
        pass





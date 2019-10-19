# -*- coding: utf-8 -*-

from odoo import api, fields, models
from ..api.CorpApi import *
from ..helper.common import *
from odoo.exceptions import UserError

class Users(models.Model):
    _inherit = 'res.users'
    _description = '企业微信员工'
    _order = 'wxwork_user_order'

    notification_type = fields.Selection(selection_add=[('wxwork','通过企业微信处理')])

    wxwork_id = fields.Char(string='企微用户ID', readonly=True)
    is_wxwork_notice =fields.Boolean('是否接收提醒', default=True)
    is_wxwork_user = fields.Boolean('企微用户', readonly=True)
    # qr_code = fields.Binary(string='个人二维码', help='员工个人二维码，扫描可添加为外部联系人', readonly=True)
    wxwork_user_order = fields.Char(
        '企微用户排序',
        default='0',
        help='部门内的排序值，默认为0。数量必须和department一致，数值越大排序越前面。值范围是[0, 2^32)',
        readonly=True,
    )

#----------------------------------------------------------
# 变更用户类型向导
#----------------------------------------------------------

class ChangeTypeWizard(models.TransientModel):
    _name = "wizard.change.user.type"
    _description = "向导变更用户类型(企业微信)"

    def _default_user_ids(self):
        user_ids = self._context.get('active_model') == 'res.users' and self._context.get('active_ids') or []
        return [
            (0, 0, {
                'user_id': user.id,
                'user_login': user.login,
                'user_name': user.name,
            })
            for user in self.env['res.users'].browse(user_ids)
        ]

    user_ids = fields.One2many('user.type.change', 'wizard_id', string='用户', default=_default_user_ids)

    def change_type_button(self):
        self.ensure_one()
        self.user_ids.change_type_button()
        if self.env.user in self.mapped('user_ids.user_id'):
            return {'type': 'ir.actions.client', 'tag': 'reload'}
        return {'type': 'ir.actions.act_window_close'}

class ChangeTypeUser(models.TransientModel):
    _name = 'user.type.change'
    _description = 'User, Change Type Wizard'

    wizard_id = fields.Many2one('wizard.change.user.type', string='Wizard', required=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', string='User', required=True, ondelete='cascade')
    user_login = fields.Char(string='登录账号', readonly=True)
    user_name = fields.Char(string='名称', readonly=True)
    choices = ([('1', '内部用户'),('8', '门户用户'),('9', '公共用户')])
    new_type = fields.Selection(choices, string='用户类型', default='1', tracking=True)

    def change_type_button(self):
        for line in self:
            if not line.new_type:
                raise UserError("在点击'更改用户类型'按钮之前，您必须修改新的用户类型")
            if line.user_id.id ==1 or line.user_id.id==2 or line.user_id.id==3 or line.user_id.id==4 or line.user_id.id==5:
                pass
            else:
                line.user_id.write({
                    'groups_id':  [(6, 0, line.new_type)]
                })
        self.write({'new_type': False})


# -*- coding: utf-8 -*-

from odoo import api, models, fields
from odoo.exceptions import UserError
# from ..models.sync_user import *

from ..models.hr_employee import EmployeeSyncUser
import logging
_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _name = 'wizard.wxwork.user'
    _description = '企业微信生成用户向导'
    _order = 'create_date'

    sync_user_result = fields.Boolean(string='用户同步结果',default=False, readonly=True )
    times = fields.Float(string='所用时间(秒)', digits=(16, 3), readonly=True)
    result = fields.Text(string='结果', readonly=True)

    def action_create_user(self):
        params = self.env['ir.config_parameter'].sudo()
        # kwargs = {
        #     'debug': params.get_param('wxwork.debug_enabled'),
        #     'employee': self.env['hr.employee'],
        #     'users': self.env['res.users'],
        # }
        if not params.get_param('wxwork.debug_enabled'):
            _logger.error("当前设置不允许从员工同步到系统用户")
            raise UserError("当前设置不允许从员工同步到系统用户 \n\n 请检查相关设置")
        else:
            self.times, self.sync_user_result, self.result = EmployeeSyncUser.sync_user(self.env['hr.employee'])


        form_view = self.env.ref('wxwork_contacts.dialog_wxwork_contacts_sync_user_result')
        return {
            'name': '员工同步系统用户结果',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wizard.wxwork.user',
            'res_id': self.id,
            'view_id': False,
            'views': [[form_view.id,'form'],],
            'type': 'ir.actions.act_window',
            # 'context': '{}',
            # 'context': self.env.context,
            'context': {'form_view_ref':'wxwork_contacts.dialog_wxwork_contacts_sync_user_result'},
            'target': 'new',#target: 打开新视图的方式，current是在本视图打开，new是弹出一个窗口打开
            # 'auto_refresh': 0, #为1时在视图中添加一个刷新功能
            # 'auto_search': False, #加载默认视图后，自动搜索
            # 'multi': False, #视图中有个更多按钮，若multi设为True, 更多按钮显示在tree视图，否则显示在form视图
        }











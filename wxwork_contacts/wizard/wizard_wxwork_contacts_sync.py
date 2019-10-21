# -*- coding: utf-8 -*-

from odoo import api, models, fields
from odoo.exceptions import UserError
from ..models.sync import *

class ResConfigSettings(models.TransientModel):
    _name = 'wizard.wxwork.contacts'
    _description = '企业微信同步向导'
    _order = 'create_date'

    image_sync_result = fields.Boolean(string='图片同步结果', default=False, readonly=True)
    department_sync_result = fields.Boolean(string='部门同步结果',default=False, readonly=True )
    employee_sync_result = fields.Boolean(string='员工同步结果',default=False, readonly=True )
    user_sync_result = fields.Boolean(string='用户同步结果',default=False, readonly=True )
    # employee_binding_user_result = fields.Boolean(string='员工绑定用户结果',default=False, readonly=True )
    times = fields.Float(string='所用时间(秒)', digits=(16, 3), readonly=True)
    result = fields.Text(string='结果', readonly=True)

    def action_sync_contacts(self):
        params = self.env['ir.config_parameter'].sudo()
        sync_hr_enabled = params.get_param('wxwork.contacts_auto_sync_hr_enabled')
        kwargs = {
            'corpid': params.get_param('wxwork.corpid'),
            'secret': params.get_param('wxwork.contacts_secret'),
            'debug': params.get_param('wxwork.debug_enabled'),
            'department_id': params.get_param('wxwork.contacts_sync_hr_department_id'),
            'sync_hr': params.get_param('wxwork.contacts_auto_sync_hr_enabled'),
            # 'sync_user': params.get_param('wxwork.contacts_sync_user_enabled'),
            'img_path': params.get_param('wxwork.contacts_img_path'),
            'department': self.env['hr.department'],
            'employee': self.env['hr.employee'],
            # 'users': self.env['res.users'],
        }

        if not sync_hr_enabled:
            raise UserError('提示：当前设置不允许从企业微信同步到HR \n\n 请修改相关的设置')
        else:
            self.times, statuses, self.result = SyncTask(kwargs).run()
            self.image_sync_result = statuses['image_1920']
            self.department_sync_result = statuses['department']
            self.employee_sync_result = statuses['employee']
            # self.employee_binding_user_result = statuses['binding']

        form_view = self.env.ref('wxwork_contacts.dialog_wxwork_contacts_sync_result')
        return {
            'name': '更新结果',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wizard.wxwork.contacts',
            'res_id': self.id,
            'view_id': False,
            'views': [[form_view.id,'form'],],
            'type': 'ir.actions.act_window',
            # 'context': '{}',
            # 'context': self.env.context,
            'context': {'form_view_ref':'wxwork_contacts.dialog_wxwork_contacts_sync_result'},
            'target': 'new',#target: 打开新视图的方式，current是在本视图打开，new是弹出一个窗口打开
            # 'auto_refresh': 0, #为1时在视图中添加一个刷新功能
            # 'auto_search': False, #加载默认视图后，自动搜索
            # 'multi': False, #视图中有个更多按钮，若multi设为True, 更多按钮显示在tree视图，否则显示在form视图
        }











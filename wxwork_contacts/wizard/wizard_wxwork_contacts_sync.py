# -*- coding: utf-8 -*-

from odoo import api, models, fields
# from ..models.sync_image import *
from ..models.sync import *
import time


class ResConfigSettings(models.TransientModel):
    _name = 'wxwork.contacts.wizard'
    _description = '企业微信同步向导'
    _order = 'create_date'

    image_sync_result = fields.Boolean(string='图片同步结果', default=False, readonly=True)
    department_sync_result = fields.Boolean(string='部门同步结果',default=False, readonly=True )
    employee_sync_result = fields.Boolean(string='员工同步结果',default=False, readonly=True )
    user_sync_result = fields.Boolean(string='用户同步结果',default=False, readonly=True )
    employee_binding_user_result = fields.Boolean(string='员工绑定用户结果',default=False, readonly=True )
    times = fields.Float(string='所用时间(秒)', digits=(16, 3), readonly=True)
    result = fields.Text(string='结果', readonly=True)

    @api.multi
    def action_sync_contacts(self):
        params = self.env['ir.config_parameter'].sudo()
        auto_sync = params.get_param('wxwork.contacts_auto_sync_hr_enabled')
        kwargs = {
            'corpid': params.get_param('wxwork.corpid'),
            'secret': params.get_param('wxwork.contacts_secret'),
            'department_id': params.get_param('wxwork.contacts_sync_hr_department_id'),
            'auto_sync': params.get_param('wxwork.contacts_auto_sync_hr_enabled'),
            'img_path': params.get_param('wxwork.contacts_img_path'),
            'department': self.env['hr.department'],
            'employee': self.env['hr.employee'],
            'users': self.env['res.users'],
        }

        if not auto_sync:
            raise UserError('提示：当前设置不允许从企业微信同步到odoo \n\n 请修改相关的设置')
        else:
            self.times, statuses, self.result = SyncTask(kwargs).run()
            self.image_sync_result = statuses['image']
            self.user_sync_result = statuses['user']
            self.department_sync_result = statuses['department']

        form_view = self.env.ref('wxwork_contacts.dialog_wxwork_contacts_sync_result')
        return {
            'name': '更新结果',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wxwork.contacts.wizard',
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











# -*- coding: utf-8 -*-

from odoo import api, models, fields
from ..models.sync_image import *


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
        }
        times = []
        result = []
        if not auto_sync:
            raise UserError('提示：当前设置不允许从企业微信同步到odoo \n\n 请修改相关的设置')
        else:
            try:
                times_image_sync,image_sync_operate = SyncImage(kwargs).run()
                times.append(times_image_sync)
                if not image_sync_operate:
                    self.image_sync_result = False
                    result.append("企业微信图片同步失败 %s 秒" % (round(times_image_sync,3)))
                else:
                    self.image_sync_result = True
                    result.append("企业微信图片同步成功,花费时间 %s 秒" % (round(times_image_sync,3)))
            except Exception as  e:
                print('图片同步错误:%s' % repr(e))

            try:
                times_department_sync, department_sync_operate = self.env['hr.department'].sync_department()
                times.append(times_department_sync)
                if not department_sync_operate:
                    self.department_sync_result = False
                    result.append("企业微信同步部门失败")
                else:
                    self.department_sync_result = True
                    result.append("企业微信同步部门成功,花费时间%s秒" % (round(times_department_sync, 3)))
            except Exception as  e:
                print('部门同步错误:%s' % repr(e))

            try:
                times_employee_sync, employee_sync_operate = self.env['hr.employee'].sync_employee()
                times.append(times_employee_sync)
                if not employee_sync_operate:
                    self.employee_sync_result = False
                    result.append("企业微信同步员工失败")
                else:
                    self.employee_sync_result = True
                    result.append("企业微信同步员工成功,花费时间%s秒" % (round(times_employee_sync, 3)))
            except Exception as  e:
                print('员工同步错误:%s' % repr(e))


        self.times = sum(times)
        self.result = '\n'.join(result)

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











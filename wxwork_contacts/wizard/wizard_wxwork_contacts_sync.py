# -*- coding: utf-8 -*-

from odoo import api, models, fields
from odoo.http import request
from ..helper.common import Common
from odoo.exceptions import UserError
from ..models.sync import *

# department_sync_result = False

class ResConfigSettings(models.TransientModel):
    _name = 'wxwork.contacts.wizard'
    _description = '同步部门'



    department_sync_result = fields.Boolean(string='部门同步结果',default=False, readonly=True )
    department_set_result = fields.Boolean(string='设置上级部门结果',default=False, readonly=True )
    image_sync_result = fields.Boolean(string='图片同步结果',default=False, readonly=True )
    employee_sync_result = fields.Boolean(string='员工同步结果',default=False, readonly=True )
    leave_sync_result = fields.Boolean(string='离职员工同步结果',default=False, readonly=True )
    user_sync_result = fields.Boolean(string='用户同步结果',default=False, readonly=True )
    employee_binding_user_result = fields.Boolean(string='员工绑定用户结果',default=False, readonly=True )
    result = fields.Text(string='结果', readonly=True)

    @api.multi
    def action_sync_contacts(self):
        """
                同步企业微信通讯簿到Odoo
                """
        params = self.env['ir.config_parameter'].sudo()
        corpid = params.get_param('wxwork.corpid')
        secret = params.get_param('wxwork.contacts_secret')
        sync_department_id = params.get_param('wxwork.contacts_sync_hr_department_id')
        auto_sync = params.get_param('wxwork.contacts_auto_sync_hr_enabled')
        sync_img = params.get_param('wxwork.contacts_sync_img_enabled')
        img_path = params.get_param('wxwork.contacts_img_path')
        Department = self.env['hr.department']
        Employee = self.env['hr.employee']
        User = self.env['res.users']
        Groups = self.env['res.groups']
        # Provider = self.env['auth.oauth.provider']

        result = []
        if not auto_sync:
            raise UserError('提示：当前设置不允许从企业微信同步到odoo \n\n 请修改相关的设置')
        else:
            try:
                department_sync_operate = SyncDepartment(corpid, secret, sync_department_id, Department).sync_department()
                if not department_sync_operate:
                    self.department_sync_result = False
                    result.append("企业微信同步部门失败")
                else:
                    self.department_sync_result = True
                    result.append("企业微信同步部门成功")
            except BaseException:
                pass

            try:
                set_department_operate = SetDepartment(Department).set_parent_department()
                if not set_department_operate:
                    self.department_set_result = False
                    result.append("企业微信设置上级部门失败")
                else:
                    self.department_set_result = True
                    result.append("企业微信设置上级部门成功")
            except BaseException:
                pass

            try:
                image_sync_operate = SyncImage(corpid, secret, sync_department_id, img_path).download_image()
                if not image_sync_operate:
                    self.image_sync_result = False
                    result.append("企业微信图片同步失败")
                else:
                    self.image_sync_result = True
                    result.append("企业微信图片同步成功")
            except BaseException:
                pass

            try:
                employee_sync_operate = SyncEmployee(corpid, secret, sync_department_id, Department,
                                                     Employee,sync_img,img_path).sync_employee()
                if not employee_sync_operate:
                    self.employee_sync_result = False
                    result.append("企业微信员工同步失败")
                else:
                    self.employee_sync_result = True
                    result.append("企业微信员工同步成功")

            except BaseException:
                pass

            try:
                leave_sync_operate = SyncEmployee(corpid, secret, sync_department_id, Department,
                                                  Employee,sync_img,img_path).update_leave_employee()
                if not leave_sync_operate:
                    self.leave_sync_result = False
                    result.append('企业微信离职员工同步失败')
                else:
                    self.leave_sync_result = True
                    result.append('企业微信离职员工同步成功')
            except BaseException:
                pass

            try:
                user_sync_operate = SyncEmployeeToUser(Employee, User, Groups).sync_user()
                if not user_sync_operate:
                    self.user_sync_result = False
                    result.append('企业微信同步系统用户同步失败')
                else:
                    self.user_sync_result = True
                    result.append('企业微信同步系统用户同步成功')
            except BaseException:
                pass

            try:
                employee_binding_user_operate = EmployeeBindingUser(Employee, User).binding()
                if not employee_binding_user_operate:
                    self.employee_binding_user_result = False
                    result.append('企业微信员工绑定系统用户失败')
                else:
                    self.employee_binding_user_result = True
                    result.append('企业微信员工绑定系统用户成功')
            except BaseException:
                pass


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










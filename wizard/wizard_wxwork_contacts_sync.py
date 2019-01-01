# -*- coding: utf-8 -*-

from odoo import api, fields, models
from ..helper.common import Common
from odoo.exceptions import UserError
from ..models.sync import *


class ResConfigSettings(models.TransientModel):
    _name = 'wxwork.contacts.wizard'
    _description = '同步部门'

    result = fields.Char(string='结果',readonly=True)

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
        Department = self.env['hr.department']
        Employee = self.env['hr.employee']
        User = self.env['res.users']

        if not Common(auto_sync).str_to_bool():
            raise UserError('提示：当前设置不允许从企业微信同步到odoo \n\n 请修改相关的设置')
        else:
            try:
                department_sync_operate = SyncDepartment(corpid,secret,sync_department_id,Department).sync_department()
                if not department_sync_operate:
                    raise UserError('提示：企业微信部门同步失败')
                else:
                    department_sync_status = True
            except BaseException:
                pass

            try:
                set_department_operate = SetDepartment(Department).set_parent_department()
                if not set_department_operate :
                    raise UserError('提示：设置企业微信上级部门失败')
                else:
                    set_department_status = True
            except BaseException:
                pass

            try:
                employee_sync_operate = SyncEmployee(corpid, secret, sync_department_id, Department, Employee).sync_employee()
                if not employee_sync_operate:
                    raise UserError('提示：企业微信员工同步失败')
                else:
                    employee_sync_status = True
            except BaseException:
                pass

            try:
                leave_sync_operate = SyncEmployee(corpid, secret, sync_department_id, Department, Employee).update_leave_employee()
                if not leave_sync_operate:
                    raise UserError('提示：企业微信离职员工同步失败')
                else:
                    leave_sync_status = True
            except BaseException:
                pass

            try:
                user_sync_operate = SyncEmployeeToUser(Employee,User).sync_user()
                if not user_sync_operate:
                    raise UserError('提示：企业微信同步系统用户同步失败')
                else:
                    user_sync_status = True
            except BaseException:
                pass

            # if  department_sync_status and set_department_status and employee_sync_status and  leave_sync_status:
            #     raise UserError('提示：企业微信同步成功')
            return True

# -*- coding: utf-8 -*-

from odoo import api, fields, models
from ..helper.common import Common
from odoo.exceptions import UserError
from ..models.sync import SyncDepartment,SyncEmployee


class ResConfigSettings(models.TransientModel):
    _name = 'wxwork.contacts.wizard'
    _description = '同步部门'

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

        if not Common(auto_sync).str_to_bool():
            raise UserError('提示：当前设置不允许从企业微信同步到odoo \n\n 请修改相关的设置')
        else:
            department_sync = SyncDepartment(corpid,secret,sync_department_id,Department).sync_department()
            employee_sync = SyncEmployee(corpid, secret, sync_department_id, Department, Employee).sync_employee()
            leave_sync = SyncEmployee(corpid, secret, sync_department_id, Department, Employee).update_leave_employee()
            if not department_sync :
                raise UserError('提示：企业微信部门同步失败')
            elif not employee_sync:
                raise UserError('提示：企业微信员工同步失败')
            elif not leave_sync:
                raise UserError('提示：企业微信员工离职同步失败')
            else:
                raise UserError('提示：完成企业微信的同步')




# -*- coding: utf-8 -*-


import logging

from odoo import api, fields, models
from ..helper.common import Common
from ..helper.sync_hr import Contacts
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


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
        auto_sync = params.get_param('wxwork.contacts_auto_sync_hr_enabled')
        sync_department_id = params.get_param(
            'wxwork.contacts_sync_hr_department_id')

        Department = self.env['hr.department']
        Employee = self.env['hr.employee']

        sync_del_hr = self.env['ir.config_parameter'].sudo(
        ).get_param('wxwork.contacts_sync_del_hr_enabled')

        if not Common(auto_sync).str_to_bool():
            raise UserError('提示：当前设置不允许从企业微信同步到odoo \n\n 请修改相关的设置')
        else:
            contacts_obj = Contacts(
                corpid,
                secret,
                sync_department_id,
                Department,
                Employee,
                sync_del_hr,
                )
            sync = contacts_obj.sync()
            if sync:
                # if Common(sync_user).str_to_bool():
                #     NewEmployee = self.env['hr.employee']
                #     domain = ['|', ('active', '=', False),
                #               ('active', '=', True)]
                #     employee_records = NewEmployee.search(
                #         domain + [
                #             ('is_wxwork_user', '=', True)
                #         ])
                    # # user_records = User.search(domain)
                    # # print(user_records.name)
                    # user_obj = CreateOrUpdateUserFromEmployee(employee_records)
                    # user_result = user_obj.CreateOrUpdate()
                    # print(user_result)
                    # user_result = HrEmployee.create_or_update_user_from_employee(employee_records)
                    # if str(user_result) == 'True':
                    #     raise UserError('提示：完成企业微信到Odoo的同步')
                    # elif str(user_result) == 'False':
                    #     raise UserError('提示：企业微信同步到User的失败')
                # else:
                raise UserError('提示：完成企业微信到Odoo的同步')
            else:
                raise UserError('提示：企业微信到HR的同步失败')

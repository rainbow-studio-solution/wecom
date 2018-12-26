# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models
from ..helper.common import Common

from odoo.exceptions import UserError
from ..models.hr_department import HrDepartment
from ..models.hr_employee import HrEmployee
from ..models.res_users import Users


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
        auto_sync = params.get_param('wxwork.contacts_auto_sync_hr_enabled')
        Department = self.env['hr.department']
        Employee = self.env['hr.employee']

        if not Common(auto_sync).str_to_bool():
            raise UserError('提示：当前设置不允许从企业微信同步到odoo \n\n 请修改相关的设置')
        else:
            HrDepartment.sync(Department)
            HrEmployee.sync(Employee)
            Users.sync(self.env['res.users'])
            raise UserError('提示：完成企业微信到Odoo的同步')



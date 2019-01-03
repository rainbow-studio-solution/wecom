# -*- coding: utf-8 -*-

from odoo import models, fields, api
from ..api.CorpApi import *
from ..helper.common import Common
import logging
from ..models.sync import *

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    corpid = fields.Char('企业ID', )
    contacts_secret = fields.Char('通讯录凭证密钥', )
    contacts_access_token = fields.Text('通讯录token', readonly=True, )
    contacts_auto_sync_hr_enabled = fields.Boolean(
        '允许企业微信通讯录自动更新HR', default=True)
    contacts_sync_del_hr_enabled = fields.Boolean('同步HR离职员工', default=False)
    contacts_sync_hr_department_id = fields.Integer('需同步的企业微信部门ID')
    contacts_edit_enabled = fields.Boolean(
        '允许API编辑企业微信通讯录', default=False, readonly=True)
    contacts_sync_user_enabled = fields.Boolean(
        '允许企业微信通讯录自动更新系统账号', default=False)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()

        corpid = params.get_param('wxwork.corpid')
        contacts_secret = params.get_param('wxwork.contacts_secret')
        contacts_access_token = params.get_param(
            'wxwork.contacts_access_token')
        contacts_auto_sync_hr_enabled = params.get_param(
            'wxwork.contacts_auto_sync_hr_enabled')
        contacts_sync_del_hr_enabled = params.get_param(
            'wxwork.contacts_sync_del_hr_enabled')
        contacts_sync_hr_department_id = params.get_param(
            'wxwork.contacts_sync_hr_department_id')
        contacts_edit_enabled = params.get_param(
            'wxwork.contacts_edit_enabled')
        contacts_sync_user_enabled = params.get_param(
            'wxwork.contacts_sync_user_enabled')

        res.update(
            corpid=corpid,
            contacts_secret=contacts_secret,
            contacts_access_token=contacts_access_token,
            contacts_auto_sync_hr_enabled=bool(
                Common(contacts_auto_sync_hr_enabled).str_to_bool()),
            contacts_sync_del_hr_enabled=bool(
                Common(contacts_sync_del_hr_enabled).str_to_bool()),
            contacts_sync_hr_department_id=int(contacts_sync_hr_department_id),
            contacts_edit_enabled=bool(
                Common(contacts_edit_enabled).str_to_bool()),
            contacts_sync_user_enabled=bool(
                Common(contacts_sync_user_enabled).str_to_bool()),
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            "wxwork.corpid", self.corpid)
        self.env['ir.config_parameter'].sudo().set_param(
            "wxwork.contacts_secret", self.contacts_secret)
        self.env['ir.config_parameter'].sudo().set_param(
            "wxwork.contacts_access_token", self.contacts_access_token)
        self.env['ir.config_parameter'].sudo().set_param(
            "wxwork.contacts_auto_sync_hr_enabled", str(
                self.contacts_auto_sync_hr_enabled))
        self.env['ir.config_parameter'].sudo().set_param(
            "wxwork.contacts_sync_del_hr_enabled", str(
                self.contacts_sync_del_hr_enabled))
        self.env['ir.config_parameter'].sudo().set_param(
            "wxwork.contacts_sync_hr_department_id", str(
                self.contacts_sync_hr_department_id))
        self.env['ir.config_parameter'].sudo().set_param(
            "wxwork.contacts_edit_enabled", str(self.contacts_edit_enabled))
        self.env['ir.config_parameter'].sudo().set_param(
            "wxwork.contacts_sync_user_enabled", str(
                self.contacts_sync_user_enabled))

    @api.multi
    def get_token(self):
        api = CorpApi(self.corpid, self.contacts_secret)
        self.env['ir.config_parameter'].sudo().set_param(
            "wxwork.contacts_access_token", api.getAccessToken())

    @api.multi
    def cron_sync_contacts(self):
        """
        同步通讯录任务
        :return:
        """
        params = self.env['ir.config_parameter'].sudo()
        corpid = params.get_param('wxwork.corpid')
        secret = params.get_param('wxwork.contacts_secret')
        sync_department_id = params.get_param('wxwork.contacts_sync_hr_department_id')
        auto_sync = params.get_param('wxwork.contacts_auto_sync_hr_enabled')
        Department = self.env['hr.department']
        Employee = self.env['hr.employee']
        User = self.env['res.users']
        try:
            if not Common(auto_sync).str_to_bool():
                _logger.info("任务失败提示-当前设置不允许从企业微信同步到odoo，请修改相关的设置")
            else:
                department_sync_operate = SyncDepartment(corpid, secret, sync_department_id, Department).sync_department()
                if not department_sync_operate:
                    _logger.info("任务失败提示-企业微信部门同步失败")
                else:
                    _logger.info("任务提示-企业微信部门同步成功")

                set_department_operate = SetDepartment(Department).set_parent_department()
                if not set_department_operate:
                    _logger.info("任务失败提示-设置企业微信上级部门失败")
                else:
                    _logger.info("任务提示-设置企业微信上级部门成功")

                employee_sync_operate = SyncEmployee(corpid, secret, sync_department_id, Department,
                                                     Employee).sync_employee()
                if not employee_sync_operate:
                    _logger.info("任务失败提示-企业微信员工同步失败")
                else:
                    _logger.info("任务提示-企业微信员工同步成功")

                leave_sync_operate = SyncEmployee(corpid, secret, sync_department_id, Department,
                                                  Employee).update_leave_employee()
                if not leave_sync_operate:
                    _logger.info("任务失败提示-企业微信离职员工同步失败")
                else:
                    _logger.info("任务提示-企业微信离职员工同步成功")

                user_sync_operate = SyncEmployeeToUser(Employee, User).sync_user()
                if not user_sync_operate:
                    _logger.info("任务失败提示-企业微信同步系统用户同步失败")
                else:
                    _logger.info("任务提示-企业微信同步系统用户同步成功")

                employee_binding_user_operate = EmployeeBindingUser(Employee, User).binding()
                if not employee_binding_user_operate:
                    _logger.info("任务失败提示-企业微信员工绑定系统用户失败")
                else:
                    _logger.info("任务提示-企业微信员工绑定系统用户成功")
        except Exception:
            _logger.error("任务失败提示-定时同步企业微信通讯簿任务无法执行,请手工执行数据同步查看详细原因")

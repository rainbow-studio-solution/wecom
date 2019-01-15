# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    corpid = fields.Char("企业ID",config_parameter='wxwork.corpid')
    # contacts_secret = fields.Char("通讯录凭证密钥", config_parameter='wxwork.contacts_secret')
    # contacts_access_token = fields.Char('通讯录token', config_parameter='wxwork.contacts_access_token', readonly=True, )
    # contacts_auto_sync_hr_enabled = fields.Boolean(
    #     '允许企业微信通讯录自动更新HR', config_parameter='wxwork.contacts_auto_sync_hr_enabled', default=True)
    # contacts_sync_hr_department_id = fields.Integer('需同步的企业微信部门ID',
    #                                                 config_parameter='wxwork.contacts_sync_hr_department_id')
    # contacts_edit_enabled = fields.Boolean('允许API编辑企业微信通讯录', config_parameter='wxwork.contacts_edit_enabled',
    #                                        default=False, )
    # contacts_sync_user_enabled = fields.Boolean('允许企业微信通讯录自动更新系统账号',
    #                                             config_parameter='wxwork.contacts_sync_user_enabled', default=False)


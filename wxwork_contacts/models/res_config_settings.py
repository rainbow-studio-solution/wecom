# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from ..api.CorpApi import *
from ..models.sync import *

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    contacts_secret = fields.Char("通讯录凭证密钥", config_parameter='wxwork.contacts_secret')
    contacts_access_token = fields.Char('通讯录token', config_parameter='wxwork.contacts_access_token', readonly=True, )
    contacts_auto_sync_hr_enabled = fields.Boolean(
        '允许企业微信通讯录自动更新HR', config_parameter='wxwork.contacts_auto_sync_hr_enabled', )
    # contacts_sync_img_enabled = fields.Boolean(
    #     '允许同步企业微信图片', config_parameter='wxwork.contacts_sync_img_enabled', )
    contacts_img_path = fields.Char('企业微信图片存储路径', config_parameter='wxwork.contacts_img_path',)
    contacts_sync_hr_department_id = fields.Integer('需同步的企业微信部门ID',
                                                    config_parameter='wxwork.contacts_sync_hr_department_id')
    contacts_edit_enabled = fields.Boolean('允许API编辑企业微信通讯录', config_parameter='wxwork.contacts_edit_enabled',
                                           default=False, readonly=True,)
    contacts_sync_user_enabled = fields.Boolean('允许企业微信通讯录自动更新系统账号',
                                                config_parameter='wxwork.contacts_sync_user_enabled', default=False)

    # @api.onchange('corpid', 'contacts_secret')
    def get_token(self):
        if self.corpid == False:
            raise UserError(_("请正确填写企业ID."))
        elif self.contacts_secret  == False:
            raise UserError(_("请正确填写通讯录凭证密钥."))
        # elif self.contacts_secret.strip() == '' or self.contacts_secret.isspace() == True or self.contacts_secret is None:
        #     raise UserError(_("请正确填写通讯录凭证密钥."))
        else:
            api = CorpApi(self.corpid, self.contacts_secret)
            self.env['ir.config_parameter'].sudo().set_param(
                "wxwork.contacts_access_token", api.getAccessToken())

    def cron_sync_contacts(self):
        """
        同步通讯录任务
        :return:
        """
        params = self.env['ir.config_parameter'].sudo()
        kwargs = {
            'corpid': params.get_param('wxwork.corpid'),
            'secret': params.get_param('wxwork.contacts_secret'),
            'department_id': params.get_param('wxwork.contacts_sync_hr_department_id'),
            'sync_hr': params.get_param('wxwork.contacts_auto_sync_hr_enabled'),
            'sync_user': params.get_param('wxwork.contacts_sync_user_enabled'),
            'img_path': params.get_param('wxwork.contacts_img_path'),
            'department': self.env['hr.department'],
            'employee': self.env['hr.employee'],
            'users': self.env['res.users'],
        }

        try:
            SyncTask(kwargs).run()
        except Exception as e:
            _logger.error("任务失败提示-定时同步企业微信通讯簿任务无法执行,详细原因:%s" % (e))

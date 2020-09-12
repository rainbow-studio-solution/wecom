# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.exceptions import UserError

# from ..models.sync_user import *

from ..models.hr_employee import EmployeeSyncUser
import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _name = "wizard.wxwork.user"
    _description = "Enterprise WeChat Generation System User Guide"
    _order = "create_date"

    sync_user_result = fields.Boolean(
        string="User synchronization result", default=False, readonly=True)
    times = fields.Float(string="Elapsed time (seconds)",
                         digits=(16, 3), readonly=True)
    result = fields.Text(string="Result", readonly=True)

    def action_create_user(self):
        params = self.env["ir.config_parameter"].sudo()

        if not params.get_param("wxwork.contacts_sync_user_enabled"):
            if params.get_param("wxwork.debug_enabled"):
                _logger.warning(
                    _("The current setting does not allow synchronization from employees to system users"))
            raise UserError(
                "The current setting does not allow synchronization from employees to system users \n\n Please check related settings")
        else:
            self.times, self.sync_user_result, self.result = EmployeeSyncUser.sync_user(
                self.env["hr.employee"]
            )

        form_view = self.env.ref(
            "wxwork_users_syncing.dialog_wxwork_contacts_sync_user_result"
        )
        return {
            "name": _("Employee synchronization system user results"),
            "view_type": "form",
            "view_mode": "form",
            "res_model": "wizard.wxwork.user",
            "res_id": self.id,
            "view_id": False,
            "views": [
                [form_view.id, "form"],
            ],
            "type": "ir.actions.act_window",
            # 'context': '{}',
            # 'context': self.env.context,
            "context": {
                "form_view_ref": "wxwork_users_syncing.dialog_wxwork_contacts_sync_user_result"
            },
            "target": "new",  # target: 打开新视图的方式，current是在本视图打开，new是弹出一个窗口打开
            # 'auto_refresh': 0, #为1时在视图中添加一个刷新功能
            # 'auto_search': False, #加载默认视图后，自动搜索
            # 'multi': False, #视图中有个更多按钮，若multi设为True, 更多按钮显示在tree视图，否则显示在form视图
        }

# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)


class WizardSyncUsers(models.TransientModel):
    _name = "wizard.wecom.user"
    _description = "WeCom Generation System User Guide"
    _order = "create_date"

    sync_user_result = fields.Boolean(
        string="User synchronization result", default=False, readonly=True
    )
    times = fields.Float(string="Elapsed time (seconds)", digits=(16, 3), readonly=True)
    result = fields.Text(string="Result", readonly=True)

    def action_sync_user(self):
        params = self.env["ir.config_parameter"].sudo()
        debug = params.get_param("wecom.debug_enabled")

        times = []
        results = ""

        time, result = self.env["hr.employee"].sync_as_user()
        times.append(time)

        if len(result) != 0:
            results += result + "\n"

        self.times = sum(times)
        self.result = results

        form_view = self.env.ref(
            "wecom_hr_syncing.dialog_wecom_contacts_sync_user_result"
        )
        return {
            "name": _("Employee synchronization system user results"),
            "view_type": "form",
            "view_mode": "form",
            "res_model": "wizard.wecom.user",
            "res_id": self.id,
            "view_id": False,
            "views": [
                [form_view.id, "form"],
            ],
            "type": "ir.actions.act_window",
            # 'context': '{}',
            # 'context': self.env.context,
            "context": {
                "form_view_ref": "wecom_hr_syncing.dialog_wecom_contacts_sync_user_result"
            },
            "target": "new",  # target: 打开新视图的方式，current是在本视图打开，new是弹出一个窗口打开
            # 'auto_refresh': 0, #为1时在视图中添加一个刷新功能
            # 'auto_search': False, #加载默认视图后，自动搜索
            # 'multi': False, #视图中有个更多按钮，若multi设为True, 更多按钮显示在tree视图，否则显示在form视图
        }

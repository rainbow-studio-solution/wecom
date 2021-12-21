# -*- coding: utf-8 -*-

import logging
from odoo import api, models, fields, _
from odoo.exceptions import UserError, Warning

from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException

_logger = logging.getLogger(__name__)


class WizardSyncContacts(models.TransientModel):
    _name = "wizard.wecom.contacts"
    _description = "WeCom synchronization wizard"
    _order = "create_date"

    image_sync_result = fields.Boolean(
        string="Picture synchronization result",
        default=False,
        readonly=True,
    )
    department_sync_result = fields.Boolean(
        string="Department synchronization result",
        default=False,
        readonly=True,
    )
    department_tag_sync_result = fields.Boolean(
        string="Department Tag synchronization results",
        default=False,
        readonly=True,
    )
    employee_sync_result = fields.Boolean(
        string="Employee synchronization results",
        default=False,
        readonly=True,
    )
    employee_tag_sync_result = fields.Boolean(
        string="Employee Tag synchronization results",
        default=False,
        readonly=True,
    )
    user_sync_result = fields.Boolean(
        string="User synchronization result",
        default=False,
        readonly=True,
    )

    times = fields.Float(
        string="Elapsed time (seconds)",
        digits=(16, 3),
        readonly=True,
    )
    result = fields.Text(string="Result", readonly=True)

    def action_sync_contacts(self):
        """
        启动同步
        """
        params = self.env["ir.config_parameter"].sudo()

        # 获取 标记为 企业微信组织 的公司
        companies = (
            self.sudo()
            .env["res.company"]
            .search([(("is_wecom_organization", "=", True))])
        )

        if not companies:
            action = {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Tips"),
                    "type": "info",
                    "message": _("There are currently no companies to synchronize."),
                    "sticky": False,
                },
            }
            return action

        times = []
        results = ""
        for company in companies:
            # 遍历公司，获取公司是否绑定了通讯录应用 以及 是否允许同步hr的参数
            if company.contacts_app_id:
                app_config = self.env["wecom.app_config"].sudo()
                sync_hr_enabled = app_config.get_param(
                    company.contacts_app_id.id, "contacts_auto_sync_hr_enabled"
                )  # 允许企业微信通讯簿自动更新为HR的标识

                if sync_hr_enabled:
                    time, result = self.env["wecom.sync_task"].run(company)
                    times.append(time)

                    for re in result:
                        results += re + "\n"
                else:
                    _logger.warning(
                        _("Company [%s] is not allowed to synchronize HR.")
                        % company.name
                    )
                    results += (
                        _("Company [%s] is not allowed to synchronize HR.")
                        % company.name
                    )
            else:
                results += (
                    _(
                        "The company [%s] does not bind the WeCom contacts application. Please go to the setting page to bind it."
                    )
                    % company.name
                )
        self.times = sum(times)
        self.result = results

        form_view = self.env.ref("wecom_hrm_syncing.dialog_wecom_contacts_sync_result")
        return {
            "name": _("Update result"),
            "view_type": "form",
            "view_mode": "form",
            "res_model": "wizard.wecom.contacts",
            "res_id": self.id,
            "view_id": False,
            "views": [
                [form_view.id, "form"],
            ],
            "type": "ir.actions.act_window",
            # 'context': '{}',
            # 'context': self.env.context,
            "context": {
                "form_view_ref": "wecom_hrm_syncing.dialog_wecom_contacts_sync_result"
            },
            "target": "new",  # target: 打开新视图的方式，current是在本视图打开，new是弹出一个窗口打开
            # 'auto_refresh': 0, #为1时在视图中添加一个刷新功能
            # 'auto_search': False, #加载默认视图后，自动搜索
            # 'multi': False, #视图中有个更多按钮，若multi设为True, 更多按钮显示在tree视图，否则显示在form视图
        }

    def reload(self):
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }

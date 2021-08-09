# -*- coding: utf-8 -*-

from odoo.addons.wxwork_api.api.corp_api import CorpApi, CORP_API_TYPE
from odoo.addons.wxwork_api.api.abstract_api import ApiException
from odoo.addons.wxwork_api.api.error_code import Errcode
from odoo import api, models, fields, _
from odoo.exceptions import UserError, Warning
from ..models.sync_contacts import *


class WizardSyncContacts(models.TransientModel):
    _name = "wizard.wxwork.contacts"
    _description = "Enterprise WeChat synchronization wizard"
    _order = "create_date"

    image_sync_result = fields.Boolean(
        string="Picture synchronization result", default=False, readonly=True,
    )
    department_sync_result = fields.Boolean(
        string="Department synchronization result", default=False, readonly=True,
    )
    department_tag_sync_result = fields.Boolean(
        string="Department Tag synchronization results", default=False, readonly=True,
    )
    employee_sync_result = fields.Boolean(
        string="Employee synchronization results", default=False, readonly=True,
    )
    employee_tag_sync_result = fields.Boolean(
        string="Employee Tag synchronization results", default=False, readonly=True,
    )
    user_sync_result = fields.Boolean(
        string="User synchronization result", default=False, readonly=True,
    )

    times = fields.Float(
        string="Elapsed time (seconds)", digits=(16, 3), readonly=True,
    )
    result = fields.Text(string="Result", readonly=True)

    @api.model
    def check_api(self, corpid, secret):
        try:
            api = CorpApi(corpid, secret)
            self.env["ir.config_parameter"].sudo().set_param(
                "wxwork.contacts_access_token", api.getAccessToken()
            )
            return True

        except ApiException as ex:
            return False

    def action_sync_contacts(self):
        """
        启动同步
        """
        params = self.env["ir.config_parameter"].sudo()

        # 获取 标记为 企业微信组织 的公司
        companies = (
            self.sudo()
            .env["res.company"]
            .search([(("is_wxwork_organization", "=", True))])
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
            # 遍历companies
            sync_hr_enabled = company.contacts_auto_sync_hr_enabled  # 允许企业微信通讯簿自动更新为HR
            sync_avatar_enabled = company.contacts_sync_avatar_enabled  # 允许同步头像
            always_sync_avatar_enabled = (
                company.contacts_always_update_avatar_enabled
            )  # 允许总是同步头像
            corpid = company.corpid
            secret = company.contacts_secret
            department_id = company.contacts_sync_hr_department_id

            # 生成关键字参数字典
            kwargs = {
                "debug": params.get_param("wxwork.debug_enabled"),
                "img_path": params.get_param("wxwork.img_path"),
                "corpid": corpid,
                "secret": secret,
                "department_id": department_id,
                "sync_hr": sync_hr_enabled,
                "sync_avatar": sync_avatar_enabled,
                "always_sync_avatar": always_sync_avatar_enabled,
                "company": company,
                "department": self.env["hr.department"],
                "department_category": self.env["hr.department.category"],
                "employee": self.env["hr.employee"],
                "employee_category": self.env["hr.employee.category"],
            }

            if not self.check_api(corpid, secret):
                raise Warning(
                    _("Enterprise WeChat configuration is wrong, please check.")
                )
            elif sync_hr_enabled == "False" or sync_hr_enabled is None:
                raise Warning(
                    _(
                        "Tip: The current setting does not allow synchronization from enterprise WeChat to HR \n\n Please generate a user manually \n\n Please modify the related settings"
                    )
                )
            else:
                # self.times, statuses, self.result = SyncTask(kwargs).run()
                time, result = SyncTask(kwargs).run()
                times.append(time)
                results += result + "\n"
                # results.append(result)
                # results = "\n".join(result)
                # self.image_sync_result = statuses["image_1920"]  # 图片同步结果
                # self.department_sync_result = bool(statuses["department"])  # 部门同步结果
                # self.department_tag_sync_result = bool(
                #     statuses["department_category"]
                # )  # 部门标签同步结果
                # self.employee_sync_result = statuses["employee"]  # 员工同步结果
                # self.employee_tag_sync_result = bool(
                #     statuses["employee_category"]
                # )  # 员工标签同步结果

        self.times = sum(times)
        self.result = results

        form_view = self.env.ref("wxwork_hr_syncing.dialog_wxwork_contacts_sync_result")
        return {
            "name": _("Update result"),
            "view_type": "form",
            "view_mode": "form",
            "res_model": "wizard.wxwork.contacts",
            "res_id": self.id,
            "view_id": False,
            "views": [[form_view.id, "form"],],
            "type": "ir.actions.act_window",
            # 'context': '{}',
            # 'context': self.env.context,
            "context": {
                "form_view_ref": "wxwork_hr_syncing.dialog_wxwork_contacts_sync_result"
            },
            "target": "new",  # target: 打开新视图的方式，current是在本视图打开，new是弹出一个窗口打开
            # 'auto_refresh': 0, #为1时在视图中添加一个刷新功能
            # 'auto_search': False, #加载默认视图后，自动搜索
            # 'multi': False, #视图中有个更多按钮，若multi设为True, 更多按钮显示在tree视图，否则显示在form视图
        }

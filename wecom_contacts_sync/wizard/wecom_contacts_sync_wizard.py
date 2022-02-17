# -*- coding: utf-8 -*-


import logging
from odoo import api, models, fields, _
from odoo.exceptions import UserError, Warning

import pandas as pd

pd.set_option("max_colwidth", 4096)  # 设置最大列宽
pd.set_option("display.max_columns", 30)  # 设置最大列数
pd.set_option("expand_frame_repr", False)  # 当列太多时不换行
import time

from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException

_logger = logging.getLogger(__name__)


class WecomContactsSyncWizard(models.TransientModel):
    _name = "wecom.contacts.sync.wizard"
    _description = "WeCom contacts synchronization wizard"
    # _order = "create_date"

    @api.model
    def _default_company_ids(self):
        """
        默认公司
        """
        company_ids = self.env["res.company"].search(
            [("is_wecom_organization", "=", True),]
        )
        return company_ids

    sync_all = fields.Boolean(
        string="Synchronize all companies", default=True, required=True,
    )
    companies = fields.Char(string="Sync Companies", compute="_compute_sync_companies")
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        domain="[('is_wecom_organization', '=', True)]",
        store=True,
    )

    contacts_app_id = fields.Many2one(
        related="company_id.contacts_app_id", store=False,
    )

    @api.depends("sync_all")
    def _compute_sync_companies(self):
        """
        获取需要同步的公司名称
        """
        if self.sync_all:
            companies = (
                self.sudo()
                .env["res.company"]
                .search([(("is_wecom_organization", "=", True))])
            )
            companies_names = [company.name for company in companies]
            self.companies = ",".join(companies_names)
        else:
            self.companies = self.company_id.name

    @api.onchange("company_id")
    def onchange_company_id(self):
        if self.sync_all is False:
            self.companies = self.company_id.name

    @api.depends("contacts_app_id")
    def _compute_config(self):
        self.contacts_app_config_ids = self.contacts_app_id.app_config_ids.filtered(
            lambda x: x.key.startswith("contacts_")
        )

    contacts_app_config_ids = fields.One2many(
        "wecom.app_config",
        "app_id",
        store=False,
        string="Application Configuration",
        compute=_compute_config,
    )

    state = fields.Selection(
        [
            ("completed", "All completed"),
            ("partially", "Partially complete"),
            ("fail", "All failed"),
        ],
        "Status",
        readonly=True,
        copy=False,
        default="completed",
    )
    sync_result = fields.Text("Sync result", readonly=1)
    total_time = fields.Float(
        string="Total time(seconds)", digits=(16, 3), readonly=True,
    )

    hr_department_sync_state = fields.Selection(
        [
            ("completed", "All completed"),
            ("partially", "Partially complete"),
            ("fail", "All failed"),
        ],
        "Hr department synchronization Status",
        readonly=True,
        copy=False,
        default="completed",
    )
    hr_department_sync_times = fields.Float(
        string="Hr department synchronization time (seconds)",
        digits=(16, 3),
        readonly=True,
    )
    hr_department_sync_result = fields.Text(
        "Hr department synchronization results", readonly=1
    )

    hr_employee_sync_state = fields.Selection(
        [
            ("completed", "All completed"),
            ("partially", "Partially complete"),
            ("fail", "All failed"),
        ],
        "Hr employee synchronization Status",
        readonly=True,
        copy=False,
        default="completed",
    )
    hr_employee_sync_times = fields.Float(
        string="Hr employee synchronization time (seconds)", digits=(16, 3), readonly=True,
    )
    hr_employee_sync_result = fields.Text("Hr employee synchronization results", readonly=1)

    hr_tag_sync_state = fields.Selection(
        [
            ("completed", "All completed"),
            ("partially", "Partially complete"),
            ("fail", "All failed"),
        ],
        "Hr tag synchronization Status",
        readonly=True,
        copy=False,
        default="completed",
    )
    hr_tag_sync_times = fields.Float(
        string="Hr tag synchronization time (seconds)", digits=(16, 3), readonly=True,
    )
    hr_tag_sync_result = fields.Text("Hr tag synchronization results", readonly=1)

    def action_sync_contacts(self):
        results = []
        sync_start_time = time.time()
        if self.sync_all:
            # 同步所有公司
            companies = (
                self.sudo()
                .env["res.company"]
                .search([(("is_wecom_organization", "=", True))])
            )

            for company in companies:
                # 遍历公司
                result = self.start_sync_contacts(company)
                results.append(result)
        else:
            # 同步当前选中公司
            result = self.start_sync_contacts(self.company_id)
            results.append(result)

        sync_end_time = time.time()
        self.total_time = sync_end_time - sync_start_time
        # 处理数据

        df = pd.DataFrame(results)

        (
            self.state,
            self.hr_department_sync_state,
            self.hr_employee_sync_state,
            self.hr_tag_sync_state,
        ) = self.handle_sync_all_state(
            df
        )  # 处理同步状态

        # 处理同步结果和时间
        sync_result = ""
        hr_department_sync_result = ""
        hr_employee_sync_result = ""
        hr_tag_sync_result = ""

        hr_department_sync_times = 0
        hr_employee_sync_times = 0
        hr_tag_sync_times = 0

        for index, row in df.iterrows():
            if row["sync_state"] == "fail":
                sync_result += str(index + 1) + ":" + row["sync_result"] + "\n"
            hr_department_sync_result += (
                str(index + 1) + ":" + row["hr_department_sync_result"] + "\n"
            )
            hr_employee_sync_result += (
                str(index + 1) + ":" + row["hr_employee_sync_result"] + "\n"
            )
            hr_tag_sync_result += str(index + 1) + ":" + row["hr_tag_sync_result"] + "\n"

            hr_department_sync_times += row["hr_department_sync_times"]
            hr_employee_sync_times += row["hr_employee_sync_times"]
            hr_tag_sync_times += row["hr_tag_sync_times"]

        self.sync_result = sync_result
        self.hr_department_sync_result = hr_department_sync_result
        self.hr_employee_sync_result = hr_employee_sync_result
        self.hr_tag_sync_result = hr_tag_sync_result

        self.hr_department_sync_times = hr_department_sync_times
        self.hr_employee_sync_times = hr_employee_sync_times
        self.hr_tag_sync_times = hr_tag_sync_times

        # 显示同步结果
        form_view = self.env.ref(
            "wecom_contacts_sync.view_form_wecom_contacts_sync_result"
        )
        return {
            "name": _("Sync result"),
            "view_type": "form",
            "view_mode": "form",
            "res_model": "wecom.contacts.sync.wizard",
            "res_id": self.id,
            "view_id": False,
            "views": [[form_view.id, "form"],],
            "type": "ir.actions.act_window",
            # 'context': '{}',
            # 'context': self.env.context,
            "context": {
                "form_view_ref": "wecom_hrm_syncing.dialog_wecom_contacts_sync_result"
            },
            "target": "new",  # target: 打开新视图的方式，current是在本视图打开， new 是弹出一个窗口打开
            # 'auto_refresh': 0, #为1时在视图中添加一个刷新功能
            # 'auto_search': False, #加载默认视图后，自动搜索
            # 'multi': False, #视图中有个更多按钮，若multi设为True, 更多按钮显示在tree视图，否则显示在form视图
        }

    def start_sync_contacts(self, company):
        """
        启动同步
        """
        if company.contacts_app_id:
            result = {}
            app_config = self.env["wecom.app_config"].sudo()
            sync_hr_enabled = app_config.get_param(
                company.contacts_app_id.id, "contacts_auto_sync_hr_enabled"
            )  # 允许企业微信通讯簿自动更新为HR的标识
            if sync_hr_enabled:
                result = {"company_name": company.name, "sync_state": "completed"}

                # 同步部门
                sync_department_result = (
                    self.env["hr.department"]
                    .with_context(company_id=company)
                    .download_wecom_deps()
                )
                (
                    hr_department_sync_state,
                    hr_department_sync_times,
                    hr_department_sync_result,
                ) = self.handle_sync_task_state(sync_department_result, company)
                
                result.update(
                    {
                        "hr_department_sync_state": hr_department_sync_state,
                        "hr_department_sync_times": hr_department_sync_times,
                        "hr_department_sync_result": hr_department_sync_result,
                    }
                )

                # 同步员工
                sync_employee_result = (
                    self.env["hr.employee"]
                    .with_context(company_id=company)
                    .download_wecom_staffs()
                )
                (
                    hr_employee_sync_state,
                    hr_employee_sync_times,
                    hr_employee_sync_result,
                ) = self.handle_sync_task_state(sync_employee_result, company)
                result.update(
                    {
                        "hr_employee_sync_state": hr_employee_sync_state,
                        "hr_employee_sync_times": hr_employee_sync_times,
                        "hr_employee_sync_result": hr_employee_sync_result,
                    }
                )

                # 同步标签
                sync_tag_result = (
                    self.env["hr.employee.category"]
                    .with_context(company_id=company)
                    .download_wecom_tags()
                )
                (
                    hr_tag_sync_state,
                    hr_tag_sync_times,
                    hr_tag_sync_result,
                ) = self.handle_sync_task_state(sync_tag_result, company)
                result.update(
                    {
                        "hr_tag_sync_state": hr_tag_sync_state,
                        "hr_tag_sync_times": hr_tag_sync_times,
                        "hr_tag_sync_result": hr_tag_sync_result,
                    }
                )

            else:
                result.update(
                    {
                        "company_name": company.name,
                        "sync_state": "fail",
                        "sync_result": _(
                            "Synchronization of company [%s] failed. Reason:configuration does not allow synchronization to HR."
                        )
                        % company.name,
                        "hr_department_sync_state": "fail",
                        "hr_department_sync_times": 0,
                        "hr_department_sync_result": _(
                            "Synchronization of company [%s] failed. Reason:configuration does not allow synchronization to HR."
                        )
                        % company.name,
                        "hr_employee_sync_state": "fail",
                        "hr_employee_sync_times": 0,
                        "hr_employee_sync_result": _(
                            "Synchronization of company [%s] failed. Reason:configuration does not allow synchronization to HR."
                        )
                        % company.name,
                        "hr_tag_sync_state": "fail",
                        "hr_tag_sync_times": 0,
                        "hr_tag_sync_result": _(
                            "Synchronization of company [%s] failed. Reason:configuration does not allow synchronization to HR."
                        )
                        % company.name,
                    }
                )
            return result

    def handle_sync_all_state(self, df):
        """
        处理同步状态
        """
        all_state_rows = len(df)  # 获取所有行数
        fail_state_rows = len(df[df["sync_state"] == "fail"])  # 获取失败行数

        fail_department_state_rows = len(
            df[df["hr_department_sync_state"] == "fail"]
        )  # 获取失败行数
        fail_employee_state_rows = len(
            df[df["hr_employee_sync_state"] == "fail"]
        )  # 获取失败行数
        fail_tag_state_rows = len(df[df["hr_tag_sync_state"] == "fail"])  # 获取失败行数

        sync_state = None
        hr_department_sync_state = None
        hr_employee_sync_state = None
        hr_tag_sync_state = None

        if fail_state_rows == all_state_rows:
            sync_state = "fail"
        elif fail_state_rows > 0 and fail_state_rows < all_state_rows:
            sync_state = "partially"
        elif fail_state_rows == 0:
            sync_state = "completed"

        if fail_department_state_rows == all_state_rows:
            hr_department_sync_state = "fail"
        elif (
            fail_department_state_rows > 0
            and fail_department_state_rows < all_state_rows
        ):
            hr_department_sync_state = "partially"
        elif fail_department_state_rows == 0:
            hr_department_sync_state = "completed"

        if fail_employee_state_rows == all_state_rows:
            hr_employee_sync_state = "fail"
        elif fail_employee_state_rows > 0 and fail_employee_state_rows < all_state_rows:
            hr_employee_sync_state = "partially"
        elif fail_employee_state_rows == 0:
            hr_employee_sync_state = "completed"

        if fail_tag_state_rows == all_state_rows:
            hr_tag_sync_state = "fail"
        elif fail_tag_state_rows > 0 and fail_tag_state_rows < all_state_rows:
            hr_tag_sync_state = "partially"
        elif fail_tag_state_rows == 0:
            hr_tag_sync_state = "completed"

        return sync_state, hr_department_sync_state, hr_employee_sync_state, hr_tag_sync_state

    def handle_sync_task_state(self, result, company):
        """
        处理部门、员工、标签同步状态
        """
        df = pd.DataFrame(result)
        all_rows = len(df)  # 获取所有行数
        fail_rows = len(df[df["state"] == False])  # 获取失败行数
        print(all_rows,fail_rows)

        sync_state = None
        if fail_rows == all_rows:
            sync_state = "fail"
        elif fail_rows > 0 and fail_rows < all_rows:
            sync_state = "partially"
        elif fail_rows == 0:
            sync_state = "completed"

        sync_result = ""
        sync_times = 0
        for index, row in df.iterrows():
            sync_times += row["time"]
            sync_result += "[%s] %s \n" % (company.name,row["msg"])

        return sync_state, sync_times, sync_result

    def reload(self):
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }

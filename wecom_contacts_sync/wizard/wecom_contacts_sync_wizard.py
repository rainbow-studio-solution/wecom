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

    # HR部门
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

    # HR员工
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
        string="Hr employee synchronization time (seconds)",
        digits=(16, 3),
        readonly=True,
    )
    hr_employee_sync_result = fields.Text(
        "Hr employee synchronization results", readonly=1
    )

    # HR标签
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

    # 系统用户
    res_user_sync_state = fields.Selection(
        [
            ("completed", "All completed"),
            ("partially", "Partially complete"),
            ("fail", "All failed"),
        ],
        "User synchronization Status",
        readonly=True,
        copy=False,
        default="completed",
    )
    res_user_sync_times = fields.Float(
        string="User synchronization time (seconds)", digits=(16, 3), readonly=True,
    )
    res_user_sync_result = fields.Text("User synchronization results", readonly=1)

    # 联系人标签
    partner_tag_sync_state = fields.Selection(
        [
            ("completed", "All completed"),
            ("partially", "Partially complete"),
            ("fail", "All failed"),
        ],
        "Contact tag synchronization Status",
        readonly=True,
        copy=False,
        default="completed",
    )
    partner_tag_sync_times = fields.Float(
        string="Contact tag synchronization time (seconds)",
        digits=(16, 3),
        readonly=True,
    )
    partner_tag_sync_result = fields.Text(
        "Contact tag synchronization results", readonly=1
    )

    def wizard_sync_contacts(self):
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
                result = self.sync_contacts(company)
                results.append(result)
        else:
            # 同步当前选中公司
            result = self.sync_contacts(self.company_id)
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
            self.res_user_sync_state,
            self.partner_tag_sync_state,
        ) = self.handle_sync_all_state(
            df
        )  # 处理同步状态

        # 处理同步结果和时间
        sync_result = ""
        hr_department_sync_result = ""
        hr_employee_sync_result = ""
        hr_tag_sync_result = ""
        res_user_sync_result = ""
        partner_tag_sync_result = ""

        hr_department_sync_times = 0
        hr_employee_sync_times = 0
        hr_tag_sync_times = 0
        res_user_sync_times = 0
        partner_tag_sync_times = 0

        rows = len(df)  # 获取所有行数
        for index, row in df.iterrows():
            if row["sync_state"] == "fail":
                sync_result += self.handle_sync_result(index, rows, row["sync_result"])
            hr_department_sync_result += self.handle_sync_result(
                index, rows, row["hr_department_sync_result"]
            )
            hr_employee_sync_result += self.handle_sync_result(
                index, rows, row["hr_employee_sync_result"]
            )
            hr_tag_sync_result += self.handle_sync_result(
                index, rows, row["hr_tag_sync_result"]
            )
            res_user_sync_result += self.handle_sync_result(
                index, rows, row["res_user_sync_result"]
            )
            partner_tag_sync_result += self.handle_sync_result(
                index, rows, row["partner_tag_sync_result"]
            )

            hr_department_sync_times += row["hr_department_sync_times"]
            hr_employee_sync_times += row["hr_employee_sync_times"]
            hr_tag_sync_times += row["hr_tag_sync_times"]
            res_user_sync_times += row["res_user_sync_times"]
            partner_tag_sync_times += row["partner_tag_sync_times"]

        self.sync_result = sync_result
        self.hr_department_sync_result = hr_department_sync_result
        self.hr_employee_sync_result = hr_employee_sync_result
        self.hr_tag_sync_result = hr_tag_sync_result
        self.res_user_sync_result = res_user_sync_result
        self.partner_tag_sync_result = partner_tag_sync_result

        self.hr_department_sync_times = hr_department_sync_times
        self.hr_employee_sync_times = hr_employee_sync_times
        self.hr_tag_sync_times = hr_tag_sync_times
        self.res_user_sync_times = res_user_sync_times
        self.partner_tag_sync_times = partner_tag_sync_times

        # 显示同步结果
        form_view = self.env.ref(
            "wecom_contacts_sync.view_form_wecom_contacts_sync_result"
        )
        return {
            "name": _("Synchronize results using the wizard"),
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
                # "form_view_ref": "hrms_syncing.dialog_wecom_contacts_sync_result"
            },
            "target": "new",  # target: 打开新视图的方式，current是在本视图打开， new 是弹出一个窗口打开
            # 'auto_refresh': 0, #为1时在视图中添加一个刷新功能
            # 'auto_search': False, #加载默认视图后，自动搜索
            # 'multi': False, #视图中有个更多按钮，若multi设为True, 更多按钮显示在tree视图，否则显示在form视图
        }

    def sync_contacts(self, company):
        """
        同步通讯录
        """
        contacts_app = company.contacts_app_id
        result = contacts_app.sync_contacts()
        return result

    def handle_sync_result(self, index, rows, result):
        """
        处理同步结果
        """
        if result is None:
            return ""
        if index < rows - 1:
            result = "%s:%s \n" % (str(index + 1), result)
        else:
            result = "%s:%s" % (str(index + 1), result)
        return result

    def handle_sync_all_state(self, df):
        """
        处理同步状态
        """
        all_state_rows = len(df)  # 获取所有行数
        fail_state_rows = len(df[df["sync_state"] == "fail"])  # 获取失败行数

        fail_department_state_rows = len(
            df[df["hr_department_sync_state"] == "fail"]
        )  # 获取HR部门失败行数
        fail_employee_state_rows = len(
            df[df["hr_employee_sync_state"] == "fail"]
        )  # 获取HR员工失败行数
        fail_hr_tag_state_rows = len(
            df[df["hr_tag_sync_state"] == "fail"]
        )  # 获取HR标签失败行数
        fail_user_state_rows = len(
            df[df["res_user_sync_state"] == "fail"]
        )  # 获取系统用户失败行数
        fail_partner_tag_state_rows = len(
            df[df["res_user_sync_state"] == "fail"]
        )  # 获取联系人标签失败行数

        sync_state = None
        hr_department_sync_state = None
        hr_employee_sync_state = None
        hr_tag_sync_state = None
        res_user_sync_state = None
        partner_tag_sync_state = None

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

        if fail_hr_tag_state_rows == all_state_rows:
            hr_tag_sync_state = "fail"
        elif fail_hr_tag_state_rows > 0 and fail_hr_tag_state_rows < all_state_rows:
            hr_tag_sync_state = "partially"
        elif fail_hr_tag_state_rows == 0:
            hr_tag_sync_state = "completed"

        if fail_user_state_rows == all_state_rows:
            res_user_sync_state = "fail"
        elif fail_user_state_rows > 0 and fail_user_state_rows < all_state_rows:
            res_user_sync_state = "partially"
        elif fail_user_state_rows == 0:
            res_user_sync_state = "completed"

        if fail_partner_tag_state_rows == all_state_rows:
            partner_tag_sync_state = "fail"
        elif (
            fail_partner_tag_state_rows > 0
            and fail_partner_tag_state_rows < all_state_rows
        ):
            partner_tag_sync_state = "partially"
        elif fail_partner_tag_state_rows == 0:
            partner_tag_sync_state = "completed"

        return (
            sync_state,
            hr_department_sync_state,
            hr_employee_sync_state,
            hr_tag_sync_state,
            res_user_sync_state,
            partner_tag_sync_state,
        )

    def reload(self):
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }

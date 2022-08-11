# -*- coding: utf-8 -*-

import logging
from odoo import api, models, fields, _
from odoo.exceptions import UserError, Warning

import pandas as pd

pd.set_option("max_colwidth", 4096)  # 设置最大列宽
pd.set_option("display.max_columns", 30)  # 设置最大列数
pd.set_option("expand_frame_repr", False)  # 当列太多时不换行
import time

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

    def _default_right(self):
        return self.user_has_groups("base.group_multi_company")

    manage_multiple_companies = fields.Boolean(
        string="Manage multiple companies", readonly=True, default=_default_right,
    )
    sync_all = fields.Boolean(
        string="Synchronize all companies",
        default=False,
        required=True,
        compute="_compute_sync_all",
    )
    companies = fields.Char(string="Sync Companies", compute="_compute_sync_companies")
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        domain="[('is_wecom_organization', '=', True)]",
        store=True,
    )

    @api.depends("manage_multiple_companies")
    def _compute_sync_all(self):
        # 有管理多公司的权限，则默认同步所有公司
        if self.manage_multiple_companies:
            self.sync_all = True
        else:
            self.sync_all = False

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

    # 企微部门
    wecom_department_sync_state = fields.Selection(
        [
            ("completed", "All completed"),
            ("partially", "Partially complete"),
            ("fail", "All failed"),
        ],
        "Wecom department synchronization Status",
        readonly=True,
        copy=False,
        default="completed",
    )
    wecom_department_sync_times = fields.Float(
        string="Wecom department synchronization time (seconds)",
        digits=(16, 3),
        readonly=True,
    )
    wecom_department_sync_result = fields.Text(
        "Wecom department synchronization results", readonly=1
    )

    # 企微用户
    wecom_user_sync_state = fields.Selection(
        [
            ("completed", "All completed"),
            ("partially", "Partially complete"),
            ("fail", "All failed"),
        ],
        "Wecom user synchronization Status",
        readonly=True,
        copy=False,
        default="completed",
    )
    wecom_user_sync_times = fields.Float(
        string="Wecom user synchronization time (seconds)",
        digits=(16, 3),
        readonly=True,
    )
    wecom_user_sync_result = fields.Text(
        "Wecom user synchronization results", readonly=1
    )

    # 企微标签
    wecom_tag_sync_state = fields.Selection(
        [
            ("completed", "All completed"),
            ("partially", "Partially complete"),
            ("fail", "All failed"),
        ],
        "Wecom tag synchronization Status",
        readonly=True,
        copy=False,
        default="completed",
    )
    wecom_tag_sync_times = fields.Float(
        string="Wecom tag synchronization time (seconds)",
        digits=(16, 3),
        readonly=True,
    )
    wecom_tag_sync_result = fields.Text("Wecom tag synchronization results", readonly=1)

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
                # 遍历公司,判断是否绑定了通讯录应用
                if company.contacts_app_id:
                    result = self.sync_contacts(company)
                    results.append(result)
                else:
                    pass
        else:
            # 同步当前选中公司
            result = self.sync_contacts(self.company_id)
            results.append(result)

        sync_end_time = time.time()
        self.total_time = sync_end_time - sync_start_time

        # 使用 pandas 处理数据
        df = pd.DataFrame(results)

        # 处理同步状态
        (
            self.state,
            self.wecom_department_sync_state,
            self.wecom_user_sync_state,
            self.wecom_tag_sync_state,
        ) = self.handle_sync_all_state(df)

        # 处理同步结果
        sync_result = ""
        wecom_department_sync_result = ""
        wecom_user_sync_result = ""
        wecom_tag_sync_result = ""

        # 处理同步时间
        wecom_department_sync_times = 0
        wecom_user_sync_times = 0
        wecom_tag_sync_times = 0

        rows = len(df)  # 获取所有行数

        for index, row in df.iterrows():
            if row["sync_state"] == "fail":
                sync_result += self.handle_sync_result(index, rows, row["sync_result"])
            wecom_department_sync_result += self.handle_sync_result(
                index, rows, row["wecom_department_sync_result"]
            )
            wecom_user_sync_result += self.handle_sync_result(
                index, rows, row["wecom_user_sync_result"]
            )
            wecom_tag_sync_result += self.handle_sync_result(
                index, rows, row["wecom_tag_sync_result"]
            )

            wecom_department_sync_times += row["wecom_department_sync_times"]
            wecom_user_sync_times += row["wecom_user_sync_times"]
            wecom_tag_sync_times += row["wecom_tag_sync_times"]

        self.sync_result = sync_result
        self.wecom_department_sync_result = wecom_department_sync_result
        self.wecom_user_sync_result = wecom_user_sync_result
        self.wecom_tag_sync_result = wecom_tag_sync_result

        self.wecom_department_sync_times = wecom_department_sync_times
        self.wecom_user_sync_times = wecom_user_sync_times
        self.wecom_tag_sync_times = wecom_tag_sync_times

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
            df[df["wecom_department_sync_state"] == "fail"]
        )  # 获取HR部门失败行数
        fail_user_state_rows = len(
            df[df["wecom_user_sync_state"] == "fail"]
        )  # 获取HR员工失败行数
        fail_tag_state_rows = len(
            df[df["wecom_tag_sync_state"] == "fail"]
        )  # 获取HR标签失败行数

        sync_state = None
        wecom_department_sync_state = None
        wecom_user_sync_state = None
        wecom_tag_sync_state = None

        if fail_state_rows == all_state_rows:
            sync_state = "fail"
        elif fail_state_rows > 0 and fail_state_rows < all_state_rows:
            sync_state = "partially"
        elif fail_state_rows == 0:
            sync_state = "completed"

        # 部门
        if fail_department_state_rows == all_state_rows:
            wecom_department_sync_state = "fail"
        elif (
            fail_department_state_rows > 0
            and fail_department_state_rows < all_state_rows
        ):
            wecom_department_sync_state = "partially"
        elif fail_department_state_rows == 0:
            wecom_department_sync_state = "completed"

        # 员工
        if fail_user_state_rows == all_state_rows:
            wecom_user_sync_state = "fail"
        elif fail_user_state_rows > 0 and fail_user_state_rows < all_state_rows:
            wecom_user_sync_state = "partially"
        elif fail_user_state_rows == 0:
            wecom_user_sync_state = "completed"

        if fail_tag_state_rows == all_state_rows:
            wecom_tag_sync_state = "fail"
        elif fail_tag_state_rows > 0 and fail_tag_state_rows < all_state_rows:
            wecom_tag_sync_state = "partially"
        elif fail_tag_state_rows == 0:
            wecom_tag_sync_state = "completed"

        return (
            sync_state,
            wecom_department_sync_state,
            wecom_user_sync_state,
            wecom_tag_sync_state,
        )

    def reload(self):
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }

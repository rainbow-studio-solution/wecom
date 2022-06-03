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

class WecomUsersSyncWizard(models.TransientModel):
    _name = "wecom.users.sync.wizard"
    _description = "Create users from employees Wizard"

    @api.model
    def _default_company_ids(self):
        """
        默认公司
        """
        company_ids = self.env["res.company"].search(
            [
                ("is_wecom_organization", "=", True),
            ]
        )
        return company_ids

    sync_all = fields.Boolean(
        string="Select all companies",
        default=True,
        required=True,
    )
    companies = fields.Char(string="Selected company", compute="_compute_sync_companies")
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        domain="[('is_wecom_organization', '=', True)]",
        store=True,
    )
    send_mail = fields.Boolean(string="Send mail or message", default=True)

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
    generate_result = fields.Text("Generate result", readonly=1)
    total_time = fields.Float(
        string="Total time(seconds)",
        digits=(16, 3),
        readonly=True,
    )

    def wizard_generate_users(self):
        results = []
        start_time = time.time()
        if self.sync_all:
            # 同步所有公司
            companies = (
                self.sudo()
                .env["res.company"]
                .search([(("is_wecom_organization", "=", True))])
            )

            for company in companies:
                # 遍历公司
                result = self.batch_create_user_from_employee(company,self.send_mail)
                results.append(result)
        else:
            # 同步当前选中公司
            result = self.batch_create_user_from_employee(self.company_id,self.send_mail)
            results.append(result)
        end_time = time.time()
        self.total_time = end_time - start_time

        # 处理数据
        df = pd.DataFrame(results)

        # 显示同步结果
        form_view = self.env.ref(
            "wecom_contacts_sync.view_form_wecom_users_sync_result"
        )
        return {
            "name": _("Generate results using the wizard"),
            "view_type": "form",
            "view_mode": "form",
            "res_model": "wecom.users.sync.wizard",
            "res_id": self.id,
            "view_id": False,
            "views": [
                [form_view.id, "form"],
            ],
            "type": "ir.actions.act_window",
            # 'context': '{}',
            # 'context': self.env.context,
            "context": {
                # "form_view_ref": "wecom_hrm_syncing.dialog_wecom_contacts_sync_result"
            },
            "target": "new",  # target: 打开新视图的方式，current是在本视图打开， new 是弹出一个窗口打开
            # 'auto_refresh': 0, #为1时在视图中添加一个刷新功能
            # 'auto_search': False, #加载默认视图后，自动搜索
            # 'multi': False, #视图中有个更多按钮，若multi设为True, 更多按钮显示在tree视图，否则显示在form视图
        }

    def batch_create_user_from_employee(self,company,send_mail):
        """
        根据员工创建用户
        :param company: 公司
        :param send_mail: 是否发送邮件
        :return:
        """
        # 查询员工
        employees = self.env["hr.employee"].search(
            [
                ("company_id", "=", company.id),
                ("is_wecom_user", "=", False),
            ]
        )
        # 创建用户
        for employee in employees:
            # 遍历员工
            employee.with_context(send_mail=send_mail).batch_create_user_from_employee()
        
 
    def create_user_from_employee(self,send_mail):
        """
        根据员工创建用户
        :param send_mail: 是否发送邮件
        :return:
        """
        # employee = self.env["hr.employee"].browse(self.env.context.get("active_id"))
        # employee.with_context(send_mail=send_mail).batch_create_user_from_employee()
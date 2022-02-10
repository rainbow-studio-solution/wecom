# -*- coding: utf-8 -*-


import logging
from odoo import api, models, fields, _
from odoo.exceptions import UserError, Warning

import pandas as pd
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
        string="Total time(seconds)",
        digits=(16, 3),
        readonly=True,
    )

    department_sync_state = fields.Selection(
        [
            ("completed", "All completed"),
            ("partially", "Partially complete"),
            ("fail", "All failed"),
        ],
        "Department synchronization Status",
        readonly=True,
        copy=False,
        default="completed",
    )
    department_sync_times = fields.Float(
        string="Department synchronization time (seconds)",
        digits=(16, 3),
        readonly=True,
    )
    department_sync_result = fields.Text("Department synchronization results", readonly=1)

    employee_sync_state = fields.Selection(
        [
            ("completed", "All completed"),
            ("partially", "Partially complete"),
            ("fail", "All failed"),
        ],
        "Employee synchronization Status",
        readonly=True,
        copy=False,
        default="completed",
    )
    employee_sync_times = fields.Float(
        string="Employee synchronization time (seconds)", digits=(16, 3), readonly=True,
    )
    employee_sync_result = fields.Text("Employee synchronization results", readonly=1)

    tag_sync_state = fields.Selection(
        [
            ("completed", "All completed"),
            ("partially", "Partially complete"),
            ("fail", "All failed"),
        ],
        "Tag synchronization Status",
        readonly=True,
        copy=False,
        default="completed",
    )
    tag_sync_times = fields.Float(
        string="Tag synchronization time (seconds)", digits=(16, 3), readonly=True,
    )
    tag_sync_result = fields.Text("Tag synchronization results", readonly=1)

    def action_sync_contacts(self):
        results =[]
        sync_start_time = time.time()
        if self.sync_all:
            # 同步所有公司
            companies = (
                self.sudo()
                .env["res.company"]
                .search([(("is_wecom_organization", "=", True))])
            )

            for company in companies:
                result = self.start_sync_contacts(company)
                results.append(result)
        else:
            # 同步当前选中公司
            result = self.start_sync_contacts(self.company_id)
            results.append(result)
        
        sync_end_time = time.time()
        self.total_time = sync_end_time - sync_start_time
        # 处理数据
        pd.set_option("max_colwidth", 4096) # 设置最大列宽
        pd.set_option('display.max_columns',30) # 设置最大列数
 
        df = pd.DataFrame(results)

    

        self.state,self.department_sync_state,self.employee_sync_state,self.tag_sync_state = self.handle_sync_state(df) # 处理同步状态

        # 处理同步结果和结果
        sync_result = ""
        department_sync_result =""
        employee_sync_result = ""
        tag_sync_result = ""
        department_sync_times = 0
        employee_sync_times = 0
        tag_sync_times = 0

        
        for index, row in df.iterrows():
            if row["state"] == "fail":
                sync_result += str(index+1)+":"+row["sync_result"] + "\n"
            department_sync_result += str(index+1)+":"+row["department_sync_result"] + "\n"
            employee_sync_result += str(index+1)+":"+row["employee_sync_result"] + "\n"
            tag_sync_result += str(index+1)+":"+row["tag_sync_result"] + "\n"
            
            department_sync_times += row["department_sync_times"]
            employee_sync_times += row["employee_sync_times"]
            tag_sync_times += row["tag_sync_times"]

        self.sync_result = sync_result
        self.department_sync_result = department_sync_result
        self.employee_sync_result = employee_sync_result
        self.tag_sync_result = tag_sync_result
        
        self.department_sync_times = department_sync_times
        self.employee_sync_times = employee_sync_times
        self.employee_sync_times = employee_sync_times
        
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
            "views": [
                [form_view.id, "form"],
            ],
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

    def handle_sync_state(self,df):
        """
        处理同步状态
        """ 
        all_state_rows = len(df) # 获取所有行数
        fail_state_rows = len(df[df["state"] == "fail"]) # 获取失败行数
        fail_department_state_rows = len(df[df["department_sync_state"] == "fail"]) # 获取失败行数
        fail_employee_state_rows = len(df[df["employee_sync_state"] == "fail"]) # 获取失败行数
        fail_tag_state_rows = len(df[df["tag_sync_state"] == "fail"]) # 获取失败行数

        state = None
        department_sync_state = None
        employee_sync_state = None
        tag_sync_state = None

        if fail_state_rows == all_state_rows:            
            state = "fail"
        elif fail_state_rows > 0 and fail_state_rows < all_state_rows:
            state = "partially"
        elif fail_state_rows == 0:
            state = "completed"

        if fail_department_state_rows == all_state_rows:            
            department_sync_state = "fail"
        elif fail_department_state_rows > 0 and fail_department_state_rows < all_state_rows:
            department_sync_state = "partially"
        elif fail_department_state_rows == 0:
            department_sync_state = "completed"

        if fail_employee_state_rows == all_state_rows:            
            employee_sync_state = "fail"
        elif fail_employee_state_rows > 0 and fail_employee_state_rows < all_state_rows:
            employee_sync_state = "partially"
        elif fail_employee_state_rows == 0:
            employee_sync_state = "completed"

        if fail_tag_state_rows == all_state_rows:            
            tag_sync_state = "fail"
        elif fail_tag_state_rows > 0 and fail_tag_state_rows < all_state_rows:
            tag_sync_state = "partially"
        elif fail_tag_state_rows == 0:
            tag_sync_state = "completed"

        return state,department_sync_state,employee_sync_state,tag_sync_state

    


    def start_sync_contacts(self,company):
        """
        启动同步
        """        
        if company.contacts_app_id:
            result ={
                "company_name":company.name,
            }
            app_config = self.env["wecom.app_config"].sudo()
            sync_hr_enabled = app_config.get_param(
                company.contacts_app_id.id, "contacts_auto_sync_hr_enabled"
            )  # 允许企业微信通讯簿自动更新为HR的标识
            if sync_hr_enabled:
                sync_department_result =self.env["hr.department"].sync_department(company)
                result.update(sync_department_result)
                result.update({
                    "employee_sync_state":"fail",                    
                    "employee_sync_times":0,
                    "employee_sync_result":"",
                    "tag_sync_state":"fail",                    
                    "tag_sync_times":0,
                    "tag_sync_result":"",
                    })
            else:
                result.update({
                    "state":"fail",
                    "sync_result":_("Synchronization of company [%s] failed. Reason:configuration does not allow synchronization to HR.") % company.name,
                    "department_sync_state":"fail",                    
                    "department_sync_times":0,
                    "department_sync_result":_("Synchronization of company [%s] failed. Reason:configuration does not allow synchronization to HR.") % company.name,
                    "employee_sync_state":"fail",                    
                    "employee_sync_times":0,
                    "employee_sync_result":_("Synchronization of company [%s] failed. Reason:configuration does not allow synchronization to HR.") % company.name,
                    "tag_sync_state":"fail",                    
                    "tag_sync_times":0,
                    "tag_sync_result":_("Synchronization of company [%s] failed. Reason:configuration does not allow synchronization to HR.") % company.name,
                })
            return result

    def reload(self):
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }
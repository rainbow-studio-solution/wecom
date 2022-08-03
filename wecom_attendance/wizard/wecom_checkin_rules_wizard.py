# -*- coding: utf-8 -*-

import datetime
import time
import json
import binascii

import logging
from odoo import models, fields, api, exceptions, _
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException

_logger = logging.getLogger(__name__)


class WecomCheckinRulesWizard(models.TransientModel):
    _name = "wecom.checkin.rules.wizard"
    _description = "WeCom checkin rules wizard"

    @api.model
    def _default_company_ids(self):
        """
        默认公司
        """
        company_ids = self.env["res.company"].search(
            [("is_wecom_organization", "=", True),]
        )
        return company_ids

    select_all = fields.Boolean(
        string="Select all companies", default=False, required=True,
    )
    companies = fields.Char(string="Companies", compute="_compute_companies")
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        domain="[('is_wecom_organization', '=', True)]",
        store=True,
    )
    attendance_app_id = fields.Many2one(
        related="company_id.attendance_app_id", store=False,
    )

    @api.depends("select_all")
    def _compute_companies(self):
        """
        获取公司名称
        """
        if self.select_all:
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
        if self.select_all is False:
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
    result = fields.Text("Result", readonly=1)
    total_time = fields.Float(
        string="Total time(seconds)", digits=(16, 3), readonly=True,
    )

    def wizard_get_checkin_rules(self):
        """
        使用向导获取打卡规则
        """
        results = []
        start_time = time.time()
        if self.select_all:
            # 获取所有的公司的打卡规则
            companies = (
                self.sudo()
                .env["res.company"]
                .search([(("is_wecom_organization", "=", True))])
            )
            for company in companies:
                # 遍历公司
                result = self.get_checkin_rules(company)
                results.append(result)
        else:
            # 同步当前选中公司
            result = self.get_checkin_rules(self.company_id)
            results.append(result)

    def get_checkin_rules(self, company):
        """
        获取打卡规则
        """

    def reload(self):
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }

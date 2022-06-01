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
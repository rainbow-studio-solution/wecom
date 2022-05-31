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
        string="Synchronize all companies",
        default=True,
        required=True,
    )
    companies = fields.Char(string="Sync Companies", compute="_compute_sync_companies")
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        domain="[('is_wecom_organization', '=', True)]",
        store=True,
    )
    send_mail = fields.Boolean(string="Send mail or message", default=True)
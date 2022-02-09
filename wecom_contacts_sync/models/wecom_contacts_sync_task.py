# -*- coding: utf-8 -*-

import logging
from unicodedata import name
from odoo import api, fields, models, _
from threading import Thread
import time

_logger = logging.getLogger(__name__)


class WecomContactsSyncTask(models.TransientModel):
    _name = "wecom.contacts.sync.task"
    _description = "Wecom Synchronization task"

    def _compute_name(self):
        """
        获取名称
        """
        self.name = _("Sync address book with company name [%s]") % self.company_id.name

    # name = fields.Char(string="Name", compute="_compute_name",store=True,)
    name = fields.Char(string="Name")
    company_id = fields.Many2one("res.company", string="Company", store=True,)
    wizard_id = fields.Many2one("wecom.contacts.sync.wizard", string="Wizard")
    department_sync_state = fields.Boolean(
        string="Department synchronization result", default=False, readonly=True,
    )
    department_sync_times = fields.Float(
        string="Department synchronization time (seconds)",
        digits=(16, 3),
        readonly=True,
    )

    employee_sync_state = fields.Boolean(
        string="Employee synchronization results", default=False, readonly=True,
    )
    employee_sync_times = fields.Float(
        string="Employee synchronization time (seconds)", digits=(16, 3), readonly=True,
    )

    tag_sync_state = fields.Boolean(
        string="Tag synchronization results", default=False, readonly=True,
    )
    tag_sync_times = fields.Float(
        string="Tag synchronization time (seconds)", digits=(16, 3), readonly=True,
    )

    sync_result = fields.Boolean(
        string="Synchronization results", default=False, readonly=True,
    )
    sync_times = fields.Float(
        string="Synchronization time (seconds)", digits=(16, 3), readonly=True,
    )
    sync_failure_reason = fields.Text("Sync Failure Reason", readonly=1)

    def run(self, wizard_id, company):
        """
        运行同步任务
        """
        params = self.env["ir.config_parameter"].sudo()
        debug = params.get_param("wecom.debug_enabled")

        task = self.create({"wizard_id": wizard_id, "company_id": company,})
        time_summary_start = time.time()
        if company.contacts_app_id:
            app_config = self.env["wecom.app_config"].sudo()
            sync_hr_enabled = app_config.get_param(
                company.contacts_app_id.id, "contacts_auto_sync_hr_enabled"
            )  # 允许企业微信通讯簿自动更新为HR的标识

            if sync_hr_enabled == "False" or sync_hr_enabled is None:
                task.write(
                    {
                        "sync_result": _("company [%s] does not allow synchronization.")
                        % (company.name)
                    }
                )
                _logger.warning(
                    _(
                        "WeCom synchronization task: company [%s] does not allow synchronization."
                    )
                    % (company.name)
                )
            else:
                pass

        else:
            if debug:
                _logger.warning(
                    _(
                        "The company [%s] does not bind the WeCom contacts application.Please go to the setting page to bind it."
                    )
                    % company.name
                )

        time_summary_end = time.time()
        time_summary = time_summary_end - time_summary_start

        task.write(
            {"sync_times": time_summary,}
        )

        return task
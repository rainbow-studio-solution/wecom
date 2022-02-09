# -*- coding: utf-8 -*-


import logging
from odoo import api, models, fields, _
from odoo.exceptions import UserError, Warning

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
    # company_ids = fields.One2many(
    #     "res.company",
    #     "contacts_app_id",
    #     string="Companies",
    #     required=True,
    #     store=True,
    #     default=_default_company_ids
    # )
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

    task_ids = fields.One2many("wecom.contacts.sync.task", "wizard_id", string="Tasks")
    state = fields.Selection(
        [
            ("all", "All completed"),
            ("partially", "Partially complete"),
            ("fail", "All failed"),
        ],
        "Status",
        readonly=True,
        copy=False,
        default="all",
    )
    failure_reason = fields.Text("Failure Reason", readonly=1)

    def action_sync_contacts(self):
        """
        启动同步
        """
        tasks = []
        if self.sync_all:
            # 同步所有公司
            companies = (
                self.sudo()
                .env["res.company"]
                .search([(("is_wecom_organization", "=", True))])
            )
            # if not companies:
            #     action = {
            #         "type": "ir.actions.client",
            #         "tag": "display_notification",
            #         "params": {
            #             "title": _("Tips"),
            #             "type": "info",
            #             "message": _(
            #                 "There are currently no companies to synchronize."
            #             ),
            #             "sticky": False,
            #         },
            #     }
            #     return action

            for company in companies:
                task = self.env["wecom.contacts.sync.task"].run(self, company)
                tasks.append(task)
        else:
            # 同步当前选中公司
            # self.env["wecom.contacts.sync.task"].run(self.company_id)
            # vals_list.append(
            #     {"company_id": self.company_id, "wizard_id": self.id,}
            # )
            task = self.env["wecom.contacts.sync.task"].run(self, self.company_id)
            tasks.append(task)
        print(tasks)
        print("```````````")
        form_view = self.env.ref(
            "wecom_contacts_sync.view_form_wecom_contacts_sync_result"
        )

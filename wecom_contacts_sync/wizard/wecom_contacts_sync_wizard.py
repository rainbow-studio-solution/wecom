# -*- coding: utf-8 -*-


import logging
from odoo import api, models, fields, _
from odoo.exceptions import UserError, Warning

from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException

_logger = logging.getLogger(__name__)


class WecomContactsSyncWizard(models.TransientModel):
    _name = "wecom.contacts.sync.wizard"
    _description = "WeCom contacts synchronization wizard"
    _order = "create_date"

    @api.model
    def _default_company_ids(self):
        """
        默认公司
        """
        company_ids = self.env["res.company"].search([("is_wecom_organization", "=", True),])
        return company_ids
    sync_all = fields.Boolean(string="Synchronize all companies", default=True,required=True,)
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
    
    contacts_app_id = fields.Many2one(related="company_id.contacts_app_id",store=False,)


    @api.depends("contacts_app_id")
    def _compute_config(self):
        self.contacts_app_config_ids = self.contacts_app_id.app_config_ids.filtered(lambda x: x.key.startswith("contacts_"))
        
    contacts_app_config_ids = fields.One2many("wecom.app_config",
        "app_id", store=False,
        string="Application Configuration",compute=_compute_config)


    # 以下为同步结果字段

    

    def action_sync_contacts(self):
        """
        启动同步
        """
        
        if self.sync_all:
            # 同步所有公司
            companies = (
                self.sudo()
                .env["res.company"]
                .search([(("is_wecom_organization", "=", True))])
            )
            if not companies:
                action = {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": _("Tips"),
                        "type": "info",
                        "message": _("There are currently no companies to synchronize."),
                        "sticky": False,
                    },
                }
                return action
            
            for company in companies:
                self.env["wecom.sync.contacts.task"].run(company)
        else:
            # 同步当前选中公司
            self.env["wecom.sync.contacts.task"].run(self.company_id)

    
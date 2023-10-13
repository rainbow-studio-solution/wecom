# -*- coding: utf-8 -*-


from odoo.http import request
from odoo import api, fields, models, tools, _


class Company(models.Model):
    _inherit = "res.company"

    self_built_app_id = fields.Many2one(
        "wecom.apps",
        string="Self-built Application",
        domain="[('company_id', '=', current_company_id)]",
    )

    contacts_sync_app_id = fields.Many2one(
        "wecom.apps",
        string="Contacts Synchronization Application",
        domain="[('company_id', '=', current_company_id)]",
    )
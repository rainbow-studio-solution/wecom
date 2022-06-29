# -*- coding: utf-8 -*-

import base64
import os
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from odoo.modules.module import get_module_resource


class Company(models.Model):
    _inherit = "res.company"

    menu_app_id = fields.Many2one(
        "wecom.apps",
        string="Menu Application",
        # required=True,
        # default=lambda self: self.env.company,
        domain="[('company_id', '=', current_company_id)]",
    )

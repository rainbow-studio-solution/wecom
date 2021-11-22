# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.modules.module import get_module_resource


class Company(models.Model):
    _inherit = "res.company"

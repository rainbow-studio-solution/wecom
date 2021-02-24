# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class Company(models.Model):
    _inherit = "res.company"

    corpid = fields.Char("Enterprise ID",)

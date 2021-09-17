# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID, _


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )

    material_agentid = fields.Char(related="company_id.material_agentid", readonly=False)
    material_secret = fields.Char(related="company_id.material_secret", readonly=False)

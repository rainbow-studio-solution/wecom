# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )

    message_agentid = fields.Char(related="company_id.message_agentid", readonly=False)

    message_secret = fields.Char(related="company_id.message_secret", readonly=False)

    module_gamification = fields.Boolean(
        related="company_id.module_gamification", readonly=False
    )

    module_wxwork_hr_gamification_message = fields.Boolean(
        related="company_id.module_wxwork_hr_gamification_message", readonly=False
    )

    module_digest = fields.Boolean(related="company_id.module_digest", readonly=False)
    module_wxowrk_digest_message = fields.Boolean(
        related="company_id.module_wxowrk_digest_message", readonly=False
    )

    module_stock = fields.Boolean(related="company_id.module_stock", readonly=False)
    module_wxwork_stock_message = fields.Boolean(
        related="company_id.module_wxwork_stock_message", readonly=False
    )

# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    attendance_app_id = fields.Many2one(
        related="company_id.attendance_app_id", readonly=False
    )
    attendance_agentid = fields.Integer(
        related="attendance_app_id.agentid", readonly=False, default=3010011
    )

    attendance_secret = fields.Char(related="attendance_app_id.secret", readonly=False)

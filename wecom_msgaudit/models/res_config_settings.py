# -*- coding: utf-8 -*-

import base64
import os
import io
from PIL import Image
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    msgaudit_app_id = fields.Many2one(
        related="company_id.msgaudit_app_id", readonly=False
    )
    msgaudit_secret = fields.Char(related="msgaudit_app_id.secret", readonly=False)
    msgaudit_access_token = fields.Char(related="msgaudit_app_id.access_token")

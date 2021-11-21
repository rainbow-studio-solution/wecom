# -*- coding: utf-8 -*-


import io
import logging
import os

from odoo import api, fields, models, tools, _
from odoo.tools.translate import translate


class Company(models.Model):
    _inherit = "res.company"

    abbreviated_name = fields.Char("Abbreviated Name", translate=True)

    is_wecom_organization = fields.Boolean("WeCom organization", default=False)
    corpid = fields.Char("Enterprise ID", default="xxxxxxxxxxxxxxxxxx")

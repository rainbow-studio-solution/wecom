# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class Company(models.Model):
    _inherit = "res.company"

    is_wxwork_organization = fields.Boolean(
        "Enterprise wechat organization", default=False
    )
    corpid = fields.Char("Enterprise ID", default="xxxxxxxxxxxxxxxxxx")

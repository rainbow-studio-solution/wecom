# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.tools.translate import translate


class Company(models.Model):
    _inherit = "res.company"

    abbreviated_name = fields.Char("Abbreviated Name", required=True, translate=True)
    is_wxwork_organization = fields.Boolean(
        "Enterprise wechat organization", default=False
    )
    corpid = fields.Char("Enterprise ID", default="xxxxxxxxxxxxxxxxxx")

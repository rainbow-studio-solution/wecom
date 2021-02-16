# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    material_agentid = fields.Char(
        "Agent Id", config_parameter="wxwork.material_agentid", default="0000000",
    )
    material_secret = fields.Char(
        "Secret",
        config_parameter="wxwork.material_secret",
        default="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    )

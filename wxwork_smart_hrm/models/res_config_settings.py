# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID, _


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    corpid = fields.Char(
        "Enterprise ID", config_parameter="wxwork.corpid", default="xxxxxxxxxxxxxxxxxx",
    )
    debug_enabled = fields.Boolean("Turn on debug mode", default=True)
    module_wxwork_auth_oauth = fields.Boolean(
        "Use Enterprise weChat scan code to verify login (OAuth)",
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ir_config = self.env["ir.config_parameter"].sudo()

        debug_enabled = (
            True if ir_config.get_param("wxwork.debug_enabled") == "True" else False
        )

        res.update(debug_enabled=debug_enabled,)
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ir_config = self.env["ir.config_parameter"].sudo()
        ir_config.set_param("wxwork.debug_enabled", self.debug_enabled or "False")

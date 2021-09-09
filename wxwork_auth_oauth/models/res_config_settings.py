# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    module_wxwork_auth_oauth_patch_for_rainbow = fields.Boolean(
        string="After installing the rainbow theme, the patch certified by the third party will be displayed normally."
    )

# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    corpid = fields.Char("企业ID", config_parameter='wxwork.corpid')
    debug_enabled = fields.Boolean('开启调试模式',
                                   config_parameter='wxwork.debug_enabled', default=True)

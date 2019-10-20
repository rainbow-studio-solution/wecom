# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    attendance_secret = fields.Char("打卡凭证密钥", config_parameter='wxwork.attendance_secret')
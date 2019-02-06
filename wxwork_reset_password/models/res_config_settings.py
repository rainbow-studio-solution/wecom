# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    qr_reset_password_uri = fields.Char('扫码重置密码地址', config_parameter='wxwork.qr_reset_password_uri')

    @api.multi
    def generate_qr_reset_password_uri(self):
        pass

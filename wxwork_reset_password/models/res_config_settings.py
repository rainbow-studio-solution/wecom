# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    auth_reset_password_redirect_uri = fields.Char('重置网页授权链接回调链接地址', help='授权后重定向的回调链接地址，请使用urlencode对链接进行处理',
                                    config_parameter='wxwork.auth_reset_password_redirect_uri')
    qr_reset_password_redirect_uri = fields.Char('扫码重置链接回调链接地址', help='授权后重定向的回调链接地址，请使用urlencode对链接进行处理',
                                    config_parameter='wxwork.qr_reset_password_redirect_uri')


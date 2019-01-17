# -*- coding: utf-8 -*-

from odoo import fields, models


class AuthOAuthProvider(models.Model):
    _inherit = 'auth.oauth.provider'

    remarks = fields.Text(string="Remarks")
    identity = fields.Char(string="Identity Information")

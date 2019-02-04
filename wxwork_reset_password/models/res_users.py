# -*- coding: utf-8 -*-

from odoo import api, fields, models

class Users(models.Model):
    _inherit = 'res.users'

    def preference_wxwork_change_password(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'wxwork_change_password',
            'target': 'new',
        }
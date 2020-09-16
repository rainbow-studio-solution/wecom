# -*- coding: utf-8 -*-

from odoo import _, api, fields, models, modules, SUPERUSER_ID, tools

class Message(models.Model):
    _inherit = 'mail.message'
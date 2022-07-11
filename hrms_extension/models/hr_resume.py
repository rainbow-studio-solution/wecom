# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResumeLineType(models.Model):
    _inherit = "hr.resume.line.type"

    name = fields.Char(required=True, translate=True)

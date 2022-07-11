# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID


class ApplicantCategory(models.Model):
    _inherit = "hr.applicant.category"

    name = fields.Char("Tag Name", required=True, translate=True)

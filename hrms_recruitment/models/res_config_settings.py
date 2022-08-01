# -*- coding: utf-8 -*-


from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = ["res.config.settings"]

    module_hrms_recruitment_survey = fields.Boolean(string="Interview Forms")


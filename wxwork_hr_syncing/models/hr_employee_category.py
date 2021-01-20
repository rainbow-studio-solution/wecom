# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class EmployeeCategory(models.Model):
    _inherit = "hr.employee.category"

    def sync_wxwork_contacts_tags(self):
        pass

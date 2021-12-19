# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class HrEmployeePrivate(models.Model):
    _inherit = "hr.employee"

    def wecom_event_change_contact_user(self, type):
        """ """
        xml_tree = self.env.context.get("xml_tree")
        company_id = self.env.context.get("company_id")
        print("hr.employee", type, company_id.name)

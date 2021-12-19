# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class HrEmployeePrivate(models.Model):
    _inherit = "hr.employee"

    def wecom_event_change_contact_user(self, type):
        """
        
        """
        # xml_tree = self.env.context.get("xml_tree")
        # company = self.env.context.get("company")
        # print("res.users", type, company.name)
        print("res.users", type)


# -*- coding: utf-8 -*-

from odoo import api, models, fields, _, SUPERUSER_ID
from odoo.exceptions import AccessError


class User(models.Model):
    _inherit = ["res.users"]

    def wecom_event_change_contact_user(self, type):
        """ """
        xml_tree = self.env.context.get("xml_tree")
        company_id = self.env.context.get("company_id")
        print("res.users", type, company_id.name)
        # print(
        #     "res.users", type,
        # )

# -*- coding: utf-8 -*-

import json
from odoo import api, fields, models, tools, _
from odoo.addons.base.models.res_users import check_identity


class ResUserMenuItems(models.Model):
    _name = "res.user.menuitems"
    _description = "User menu items"

    company_id = fields.Many2one(
        string="Company", comodel_name="res.company", ondelete="cascade", readonly=True
    )

    enable_odoo_account = fields.Boolean(string="Enable Odoo Account", default=False)
    enable_lock_screen = fields.Boolean(string="Enable lock screen", default=True)
    enable_developer_tool = fields.Boolean(
        string="Enable Developer Tools", default=True
    )
    enable_documentation = fields.Boolean(string="Enable Documentation", default=True)
    enable_support = fields.Boolean(string="Enable Support", default=True)


    def _get_or_create_menuitems(self, id):
        domain = [("company_id", "=", id)]
        vals = {"company_id": id}
        menuitem = self.search(domain, limit=1)
        if not menuitem:
            menuitem = self.create(vals)
        return menuitem

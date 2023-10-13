# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID, _


class IrConfigParameter(models.Model):
    _inherit = "ir.config_parameter"

    @api.model
    def get_coca_params(self):
        # get_rainbow_params
        params = self.sudo().search_read(
            [("key", "=like", "web_theme%")], fields=["key", "value"], limit=None
        )
        return params if params else None

    @api.model
    def get_display_company_name(self):
        display_company_name = self.sudo().get_param("web_theme.display_company_name")  # type: ignore
        # print("display_company_name", display_company_name)
        if display_company_name:
            return display_company_name
        else:
            return False

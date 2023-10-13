# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
import logging

_logger = logging.getLogger(__name__)


class Module(models.Model):
    _inherit = "ir.module.module"

    @api.model
    def check_wecom_addons_exist(self, addon_name=None):
        """
        检查 企微 addon 是否存在
        """
        addon = self.sudo().search([("name", "=", addon_name)])

        if not addon:
            # return {
            #     "exist": False,
            #     "moduleId": 0,
            # }
            return False
        else:
            # addon.button_install()
            # return {
            #     "exist": True,
            #     "moduleId": addon.id,
            # }
            return True

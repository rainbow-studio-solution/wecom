# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class Module(models.Model):
    _inherit = "ir.module.module"

    def wxwork_check_module_installed(self, modules_name):
        # modules 输入参数是个 list，如 ['base', 'sale']
        module = self.sudo().search([("name", "=", modules_name)])
        if not module or module.state != "installed":
            return False
        else:
            return True

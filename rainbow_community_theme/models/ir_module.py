# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
import logging
_logger = logging.getLogger(__name__)


class Module(models.Model):
    _inherit = "ir.module.module"

    @api.model
    def get_module_installation_status(self, domain=None, fields=None):
        record = self.sudo().search_read(domain, fields)
        if len(record) == 0:
            return False
        else:
            if record[0]['state'] != 'installed':
                return False
            else:
                return True

    def check_module_installed(self, modules_name):
        # modules 输入参数是个 list，如 ['base', 'sale']
        module = self.sudo().search([('name', '=', modules_name)])
        if not module or module.state != 'installed':
            return False
        else:
            return True

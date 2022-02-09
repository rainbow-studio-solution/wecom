# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _

class IrModelData(models.Model):
    _inherit = "ir.model.data"

    @api.model
    def get_object_reference(self, module, xml_id):
        """Returns (model, res_id) corresponding to a given module and xml_id (cached) or raise ValueError if not found"""
        return self._xmlid_lookup("%s.%s" % (module, xml_id))[1:3]
# -*- coding: utf-8 -*-

import json
from odoo import api, models
from odoo.http import request
from odoo.tools import ustr

class IrActionsActWindow(models.Model):
    _inherit = "ir.actions.act_window"

    @api.model
    def get_model_name_by_action_id(self, action_id):
        """
        res_model: 模型名称
        """
        result = {}
        data_dic = self.env['ir.actions.act_window'].browse(action_id).read()[0]
        result.update({
            "id": data_dic.get("id"),
            "name": data_dic.get("name"),
            "type": data_dic.get("type"),
            "xml_id": data_dic.get("xml_id"),
            "context": data_dic.get("context"),
            "res_model": data_dic.get("res_model"),
        })
        # print(result)
        return result
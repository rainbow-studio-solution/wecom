# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.translate import _

# PARAMS = [
#     ('wxwork.corpid', 'xxxxxxxxxxxxxxxxxx'),
#     ('wxwork.contacts_secret', 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'),
#     ('wxwork.contacts_access_token', ""),
#     ('wxwork.contacts_auto_sync_enabled','False'),
#     ('wxwork.contacts_sync_department_id', "1"),
#     ('wxwork.contacts_edit_enabled', "False"),
#     ('wxwork.contacts_sync_del_enabled', "False"),
# ]


# def get_wxwork_parameters_env(env):
#     res = {}
#     for param, default in PARAMS:
#         value = env['ir.config_parameter'].sudo().get_param(param, default)
#         res[param] = value.strip()
#     return res
#
#
# class IrConfigParameter(models.Model):
#     _inherit = 'ir.config_parameter'
#
#     @api.model
#     def get_wxwork_parameters(self):
#         res = {}
#         for param, default in PARAMS:
#             value = self.env['ir.config_parameter'].sudo(
#             ).get_param(param, default)
#             res[param] = value.strip()
#         return res
#
#     @api.model
#     def create_wxwork_parameters(self):
#         for param, default in PARAMS:
#             if not self.env['ir.config_parameter'].sudo().get_param(param):
#                 self.env['ir.config_parameter'].sudo(
#                 ).set_param(param, default or ' ')

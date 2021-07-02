# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class Users(models.Model):
    _inherit = "res.users"
    _description = "Enterprise WeChat system users"
    _order = "wxwork_user_order"

    # notification_type = fields.Selection(
    #     selection_add=[("wxwork", "Handle by Enterprise WeChat")],
    #     ondelete={"wxwork": "set default"},
    #     required=True,
    # )


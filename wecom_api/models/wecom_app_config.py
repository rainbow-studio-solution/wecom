# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class WeComAppConfig(models.Model):
    # 参考 ir.config_parameter 模型
    _name = "wecom.app_config"
    # _inherit = "ir.config_parameter"
    _description = "Wecom Application Configuration"
    _rec_name = "key"
    # _order = "key"

    app_id = fields.Many2one("wecom.apps", string="Application", copy=False)
    key = fields.Char(required=True,)
    value = fields.Text(required=True)

    _sql_constraints = [
        (
            "app_id_key_uniq",
            "unique (app_id,key)",
            _("The key of each application must be unique !"),
        )
    ]

# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class WeComAppConfig(models.Model):
    # 参考 ir.config_parameter 模型
    _name = "wecom.app.config"
    _description = "Wecom Application Configuration"
    _rec_name = "key"
    _order = "key"

    app_id = fields.Many2one("wecom.apps", string="Application", required=True,)
    key = fields.Char(required=True, index=True)
    value = fields.Text(required=True)

    _sql_constraints = [("key_uniq", "unique (key)", "Key must be unique.")]


# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class WeComAppType(models.Model):
    _name = "wecom.app.type"
    _description = "Wecom Application Type"
    _order = "sequence"

    name = fields.Char(
        string="Name",
        translate=True,
        copy=False,
        required=True,
    )
    code = fields.Char(
        string="Code",
        copy=False,
        required=True,
    )
    sequence = fields.Integer(default=0, copy=True)

    _sql_constraints = [
        (
            "code_uniq",
            "unique (code)",
            _("Code must be unique !"),
        )
    ]

# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class WeComAppType(models.Model):
    _name = "wecom.app.subtype"
    _description = "Wecom Application Subtype"
    _order = "sequence"

    name = fields.Char(
        string="Name",
        translate=True,
        copy=False,
        required=True,
    )

    parent_id = fields.Many2one(
        "wecom.app.type",
        ondelete="cascade",
        string="Parent",
        index=True,
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

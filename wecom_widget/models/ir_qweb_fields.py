# -*- coding: utf-8 -*-
import markdown

from odoo import api, models, _


class MarkdownConverter(models.AbstractModel):
    _name = "ir.qweb.field.markdown"
    _description = "Qweb Field Markdown"
    _inherit = "ir.qweb.field"

    @api.model
    def value_to_html(self, value, options):
        return markdown.markdown(value)

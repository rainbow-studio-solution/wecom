# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID, _


class JsApiIneerface(models.Model):
    _name = 'wxwork.jsapi.interface'
    _order = 'name asc'
    _description = 'Enterprise WeChat JSAPI Interface'

    name = fields.Char('Interface Name', required=True, translate=True)
    function_name = fields.Char('Function Name', required=True)
    example = fields.Html(
        string='Code example',
    )
    remarks = fields.Text('Remarks', required=True, translate=True)

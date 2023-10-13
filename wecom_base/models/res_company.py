# -*- coding: utf-8 -*-


import io
import logging
import os

from odoo import api, fields, models, tools, _


class Company(models.Model):
    _inherit = "res.company"

    # 基础
    abbreviated_name = fields.Char("Abbreviated Name", translate=True)
    is_wecom_organization = fields.Boolean("WeCom organization", default=False)
    corpid = fields.Char("Corp ID")

    # 企业的jsapi_ticket
    wecom_jsapi_ticket = fields.Char("Wecom JSAPI Ticket")
    wecom_jsapi_ticket_expiration_time = fields.Datetime(
        string="Expiration time of Wecom JSAPI ticket", copy=False
    )

    
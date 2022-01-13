# -*- coding: utf-8 -*-

import base64
import os
import io
from PIL import Image
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    msgaudit_app_id = fields.Many2one(
        related="company_id.msgaudit_app_id", readonly=False
    )
    msgaudit_secret = fields.Char(related="msgaudit_app_id.secret", readonly=False)
    msgaudit_access_token = fields.Char(related="msgaudit_app_id.access_token")

    chatdata2contact_img_max_size = fields.Integer(
        "WeCom Chat data picture attached to contact's picture size",
        default=512,
        config_parameter="wecom.msgaudit.chatdata2contacts.img_max_size",
    )

    msgaudit_chatdata_api_url = fields.Char(
        "Chat data API URL",
        default="http://localhost:8000//wecom/finance/chatdata",
        config_parameter="wecom.msgaudit.msgaudit_chatdata_api_url",
    )
    msgaudit_mediadata_api_url = fields.Char(
        "Media file data API URL",
        default="http://localhost:8000//wecom/finance/mediadata",
        config_parameter="wecom.msgaudit.msgaudit_mediadata_api_url",
    )

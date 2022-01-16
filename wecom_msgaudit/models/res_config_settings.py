# -*- coding: utf-8 -*-

import base64
from email.policy import default
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

    msgaudit_sdk_proxy = fields.Boolean(string="Proxy Request", default=False,)
    msgaudit_sdk_url = fields.Char(
        string="Sdk Request Url",
        default="http://localhost:8000",
        config_parameter="wecom.msgaudit.msgaudit_sdk_url",
    )

    msgaudit_chatdata_url = fields.Char(
        "Chat data API URL",
        default="/wecom/finance/chatdata",
        config_parameter="wecom.msgaudit.msgaudit_chatdata_url",
    )
    msgaudit_mediadata_url = fields.Char(
        "Media file data API URL",
        default="/wecom/finance/mediadata",
        config_parameter="wecom.msgaudit.msgaudit_mediadata_url",
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ir_config = self.env["ir.config_parameter"].sudo()

        msgaudit_sdk_proxy = (
            True if ir_config.get_param("wecom.msgaudit_sdk_proxy") == "True" else False
        )

        res.update(msgaudit_sdk_proxy=msgaudit_sdk_proxy,)
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ir_config = self.env["ir.config_parameter"].sudo()
        ir_config.set_param(
            "wecom.msgaudit_sdk_proxy", self.msgaudit_sdk_proxy or "False"
        )

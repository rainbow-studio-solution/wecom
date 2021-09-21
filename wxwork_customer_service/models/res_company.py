# -*- coding: utf-8 -*-

import base64
import io
import logging
import os

from odoo import api, fields, models, tools, _
from odoo.tools.translate import translate


class Company(models.Model):
    _inherit = "res.company"

    customer_service_qrcode = fields.Binary("Wechat customer service QR code")

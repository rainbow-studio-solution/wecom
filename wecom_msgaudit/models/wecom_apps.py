# -*- coding: utf-8 -*-

import logging
import datetime
import werkzeug.utils
import urllib
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import base64

_logger = logging.getLogger(__name__)


class WeComApps(models.Model):
    _inherit = "wecom.apps"

    private_keys = fields.One2many(
        "wecom.msgaudit.key", "app_id", string="Session content archive key",
    )

    
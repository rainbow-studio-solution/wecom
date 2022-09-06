# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, Command, _

from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException

_logger = logging.getLogger(__name__)


class Partner(models.Model):
    _inherit = "res.partner"

    wecom_user = fields.Many2one('wecom.user',required=True)
    wecom_userid = fields.Char(
        string="WeCom User ID",
        readonly=True, related="wecom_user.userid",store=True
    )
    wecom_openid = fields.Char(
        string="WeCom OpenID",
        readonly=True,related="wecom_user.open_userid",store=True
    )
    qr_code = fields.Char(
        string="Personal QR code",
        readonly=True,related="wecom_user.qr_code",store=True
    )

    is_wecom_user = fields.Boolean(
        "Is WeCom user",
        readonly=True,
    )

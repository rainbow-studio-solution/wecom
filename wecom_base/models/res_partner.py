# -*- coding: utf-8 -*-

from odoo import fields, models, _


class Partner(models.Model):
    _inherit = "res.partner"

    wecom_userid = fields.Char(
        string="WeCom User ID",
        readonly=True,
    )
    wecom_openid = fields.Char(string="WeCom OpenID",
        readonly=True,)

    is_wecom_user = fields.Boolean(
        "Is WeCom user",
        readonly=True,
    )
    qr_code = fields.Char(
        string="Personal QR code",
        help="Personal QR code, Scan can be added as external contact",
        readonly=True,
    )
    wecom_user_order = fields.Char(
        "WeCom User sequence",
        default="0",
        help="The sort value in the department, the default is 0. The number must be the same as the department. The larger the number, the higher the order.The value range is [0, 2^32)",
        readonly=True,
    )

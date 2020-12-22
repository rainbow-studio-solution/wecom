# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class Users(models.Model):
    _inherit = "res.users"
    _description = "Enterprise WeChat system users"
    _order = "wxwork_user_order"

    notification_type = fields.Selection(
        [("wxwork", "Handle by Enterprise WeChat")], default="mail", required=True,
    )

    wxwork_id = fields.Char(string="Enterprise WeChat user ID", readonly=True,)
    is_wxwork_notice = fields.Boolean("Whether to receive reminders", default=True,)
    is_wxwork_user = fields.Boolean("Is an enterprise WeChat user", readonly=True,)
    # qr_code = fields.Binary(string='个人二维码', help='员工个人二维码，扫描可添加为外部联系人', readonly=True)
    wxwork_user_order = fields.Char(
        "Enterprise WeChat ranking",
        default="0",
        help="The sort value in the department, the default is 0. The number must be the same as the department. The larger the number, the higher the order.The value range is [0, 2^32)",
        readonly=True,
    )

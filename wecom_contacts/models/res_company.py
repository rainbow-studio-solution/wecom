# -*- coding: utf-8 -*-


from odoo.http import request
from odoo import api, fields, models, tools, _
from odoo.tools.translate import translate


class Company(models.Model):
    _inherit = "res.company"

    # 通讯录
    contacts_app_id = fields.Many2one(
        "wecom.apps",
        string="Contacts Application",
        # required=True,
        # default=lambda self: self.env.company,
        domain="[('company_id', '=', current_company_id)]",
    )

    wecom_contacts_join_qrcode_enabled = fields.Boolean(
        string="Enable to join the enterprise QR code", default=True, copy=False,
    )
    wecom_contacts_join_qrcode = fields.Char(
        string="Join enterprise wechat QR code", copy=False, readonly=True,
    )
    wecom_contacts_join_qrcode_size_type = fields.Selection(
        [
            ("1", "171px x 171px"),
            ("2", "399px x 399px"),
            ("3", "741px x 741px"),
            ("4", "2052px x 2052px"),
        ],
        string="Join enterprise wechat QR code  size type",
        default="2",
        required=True,
    )
    wecom_contacts_join_qrcode_last_time = fields.Datetime(
        string="Get the last time of QR code (UTC)", copy=False,
    )


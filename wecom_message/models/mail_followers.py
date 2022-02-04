# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Followers(models.Model):
    _inherit = ["mail.followers"]

    wecom_userid = fields.Char(string="WeCom User ID", readonly=True,)

    is_wecom_user = fields.Boolean("Is WeCom user", readonly=True,)


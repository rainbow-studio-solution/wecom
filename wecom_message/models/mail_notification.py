# -*- coding: utf-8 -*-

from odoo import fields, models


class MailNotification(models.Model):
    _inherit = "mail.notification"

    is_wecom_message = fields.Boolean("WeCom Message")

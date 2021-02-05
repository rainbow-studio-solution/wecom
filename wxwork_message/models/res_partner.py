# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID, _


class Partner(models.Model):
    _inherit = "res.partner"

    def _wxwork_notice_send(self, email_from, subject, body, on_error=None):
        for partner in self.filtered("wxwork"):
            tools.email_send(email_from, [partner.email], subject, body, on_error)
        return True

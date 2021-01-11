# -*- coding: utf-8 -*-

import base64
import logging


from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class MailTemplate(models.Model):
    _inherit = "mail.template"

    def send_mail(
        self,
        res_id,
        force_send=False,
        raise_exception=False,
        email_values=None,
        notif_layout=False,
    ):
        values = self.generate_email(
            res_id,
            [
                "subject",
                "body_html",
                "email_from",
                "email_to",
                "partner_to",
                "email_cc",
                "reply_to",
                "scheduled_date",
            ],
        )
        print(res_id.login)
        return super(MailTemplate, self).send_mail(
            res_id,
            force_send=False,
            raise_exception=False,
            email_values=None,
            notif_layout=False,
        )

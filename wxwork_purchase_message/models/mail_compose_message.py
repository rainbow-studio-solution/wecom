# -*- coding: utf-8 -*-

from odoo import models


class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

    def send_mail(self, auto_commit=False):
        if not self.env.user.wecom_id:
            is_wecom_message = False
        else:
            is_wecom_message = True

        self.with_context(is_wecom_message=is_wecom_message)

        if self.env.context.get("mark_rfq_as_sent") and self.model == "purchase.order":
            self = self.with_context(
                mail_notify_author=self.env.user.partner_id in self.partner_ids
            )
        return super(MailComposeMessage, self).send_mail(auto_commit=auto_commit)

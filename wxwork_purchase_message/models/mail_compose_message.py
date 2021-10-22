# -*- coding: utf-8 -*-

from odoo import models


class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

    def send_mail(self, auto_commit=False):

        if not self.env.user.wxwork_id:
            is_wxwork_message = False
        else:
            is_wxwork_message = True

        if self.env.context.get("mark_rfq_as_sent") and self.model == "purchase.order":
            self = self.with_context(
                mail_notify_author=self.env.user.partner_id in self.partner_ids
            )
        return super(MailComposeMessage, self).send_mail(
            auto_commit=auto_commit, is_wxwork_message=is_wxwork_message,
        )

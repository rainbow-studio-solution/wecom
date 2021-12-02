# -*- coding: utf-8 -*-

import logging

from odoo.tools.translate import _
from odoo.tools import email_split
from odoo.exceptions import UserError

from odoo import api, fields, models


_logger = logging.getLogger(__name__)


class PortalWizardUser(models.TransientModel):
    _inherit = "portal.wizard.user"

    def _send_email(self):
        """
        向新门户用户发送通知电子邮件或企业微信消息
        """
        if self.env.user.wecom_userid:
            message_template = self.env.ref(
                "wecom_portal.message_template_data_portal_welcome"
            )
            for wizard_line in self:
                lang = wizard_line.user_id.lang
                partner = wizard_line.user_id.partner_id

                portal_url = partner.with_context(
                    signup_force_type_in_url="", lang=lang
                )._get_signup_url_for_action()[partner.id]
                partner.signup_prepare()

                if message_template:
                    message_template.with_context(
                        dbname=self._cr.dbname, portal_url=portal_url, lang=lang
                    ).send_message(wizard_line.id, force_send=True)
                else:
                    _logger.warning(
                        _(
                            "No message template found for sending message to the portal user"
                        )
                    )

        else:
            if not self.env.user.email:
                raise UserError(
                    _logger.warning(
                        _(
                            "No email template found for sending email to the portal user"
                        )
                    )
                )

            # 确定门户用户语言中的主题和主体
            template = self.env.ref("portal.mail_template_data_portal_welcome")
            for wizard_line in self:
                lang = wizard_line.user_id.lang
                partner = wizard_line.user_id.partner_id

                portal_url = partner.with_context(
                    signup_force_type_in_url="", lang=lang
                )._get_signup_url_for_action()[partner.id]
                partner.signup_prepare()

                if template:
                    template.with_context(
                        dbname=self._cr.dbname, portal_url=portal_url, lang=lang
                    ).send_mail(wizard_line.id, force_send=True)
                else:
                    _logger.warning(
                        "No email template found for sending email to the portal user"
                    )

        return True

# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import cache
from ...wxwork_api.wx_qy_api.CorpApi import *

from odoo.addons.auth_signup.models.res_partner import SignupError, now

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = "res.users"

    def action_reset_password(self):
        """ create signup token for each user, and send their signup url by email """
        if self.env.context.get("install_mode", False):
            return
        if self.filtered(lambda user: not user.active):
            raise UserError(_("You cannot perform this action on an archived user."))
        # prepare reset password signup
        create_mode = bool(self.env.context.get("create_user"))

        # no time limit for initial invitation, only for reset password
        expiration = False if create_mode else now(days=+1)

        self.mapped("partner_id").signup_prepare(
            signup_type="reset", expiration=expiration
        )

        # send email to users with their signup url
        template = False
        if create_mode:
            try:
                template = self.env.ref(
                    "auth_signup.set_password_email", raise_if_not_found=False
                )
            except ValueError:
                pass
        if not template:
            template = self.env.ref("auth_signup.reset_password_email")
        assert template._name == "mail.template"

        template_values = {
            "email_to": "${object.email|safe}",
            "email_cc": False,
            "auto_delete": True,
            "partner_to": False,
            "scheduled_date": False,
        }
        template.write(template_values)
        for user in self:
            if not user.email and user.notification_type != "wxwork":
                raise UserError(
                    _("Cannot send email: user %s has no email address.", user.name)
                )

            # TDE FIXME: make this template technical (qweb)
            with self.env.cr.savepoint():
                force_send = not (self.env.context.get("import_file", False))
                template.send_mail(user.id, force_send=force_send, raise_exception=True)
            if user.notification_type != "wxwork":
                _logger.info(
                    _("Password reset email sent for user <%s> to <%s>"),
                    user.login,
                    user.email,
                )
            else:
                _logger.info(
                    _(
                        "Password reset Enterprise WeChat message sent to the user <%s> to <%s>"
                    ),
                    user.login,
                    user.email,
                )


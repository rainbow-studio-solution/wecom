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
        # 准备重置密码注册
        create_mode = bool(self.env.context.get("create_user"))

        # 初次邀请没有时间限制，仅重设密码
        expiration = False if create_mode else now(days=+1)

        self.mapped("partner_id").signup_prepare(
            signup_type="reset", expiration=expiration
        )

        template = False
        if self.notification_type != "wxwork":
            # 通过注册网址向用户发送电子邮件
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
        else:
            # 通过注册网址向用户发送企业微信消息
            if create_mode:
                try:
                    template = self.env.ref(
                        "wxwork_message.wxwork_set_password_message",
                        raise_if_not_found=False,
                    )
                except ValueError:
                    pass
            if not template:
                template = self.env.ref("wxwork_message.wxwork_reset_password_message")
            assert template._name == "wxwork.message.template"

            template_values = {
                # "email_to": "${object.email|safe}",
                "email_to": "${object.wxwork_id|safe}",
                "email_cc": False,
                "auto_delete": True,
                "partner_to": False,
                "scheduled_date": False,
            }
            template.write(template_values)

        for user in self:
            if user.notification_type != "wxwork":
                if not user.email:
                    raise UserError(
                        _("Cannot send email: user %s has no email address.", user.name)
                    )

                # TDE FIXME：使此模板具有技术性（qweb）
                with self.env.cr.savepoint():
                    force_send = not (self.env.context.get("import_file", False))
                    template.send_mail(
                        user.id, force_send=force_send, raise_exception=True
                    )
                _logger.info(
                    _("Password reset email sent for user <%s> to <%s>"),
                    user.login,
                    user.email,
                )
            else:
                # 通过注册网址向用户发送企业微信消息
                if not user.wxwork_id:
                    raise UserError(
                        _(
                            "Cannot send user %s has no Enterprise WeChat user id.",
                            user.name,
                        )
                    )
                with self.env.cr.savepoint():
                    force_send = not (self.env.context.get("import_file", False))
                    template.send_message(
                        user.id, force_send=force_send, raise_exception=True
                    )
                _logger.info(
                    _(
                        "Password reset Enterprise WeChat message sent to the user <%s> to <%s>"
                    ),
                    user.login,
                    user.wxwork_id,
                )

# -*- coding: utf-8 -*-

import json
import requests
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.addons.base.models.ir_mail_server import MailDeliveryException
from odoo.addons.auth_signup.models.res_partner import SignupError, now

from odoo.exceptions import AccessDenied

import logging

_logger = logging.getLogger(__name__)

from odoo.http import request


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def wxwrok_auth_oauth(self, provider, params):
        """
        允许一键登录和扫码登录且标记了企业微信的用户登录系统
        :param provider:
        :param params:
        :return:
        """
        wxwork_web_auth_endpoint = "https://open.weixin.qq.com/connect/oauth2/authorize"
        wxwork_qr_auth_endpoint = "https://open.work.weixin.qq.com/wwopen/sso/qrConnect"

        wxwork_providers = (
            self.env["auth.oauth.provider"].sudo().search([("id", "=", provider),])
        )

        if (
            wxwork_web_auth_endpoint in wxwork_providers["auth_endpoint"]
            or wxwork_qr_auth_endpoint in wxwork_providers["auth_endpoint"]
        ):
            # 扫码登录
            oauth_userid = params["UserId"]
            oauth_user = self.search(
                [
                    # ("oauth_uid", "=", oauth_userid),
                    ("wxwork_id", "=", oauth_userid),
                    ("is_wxwork_user", "=", True),
                    ("active", "=", True),
                ]
            )
            if not oauth_user or len(oauth_user) > 1:
                return AccessDenied
            return (self.env.cr.dbname, oauth_user.login, oauth_userid)
        else:
            return AccessDenied

    @api.model
    def _check_credentials(self, password, env):
        # password为企业微信的用户ID
        try:
            return super(ResUsers, self)._check_credentials(password, env)
        except AccessDenied:
            res = self.sudo().search(
                [("id", "=", self.env.uid), ("wxwork_id", "=", password)]
            )
            if not res:
                raise

    def action_reset_password(self):
        """ 
        为每个用户创建注册令牌，并通过企业微信消息发送其注册网址 
        """
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

        # 通过注册网址向用户发送电子邮件或企业微信消息

        # 邮件模板
        mail_template = False
        if create_mode:
            try:
                mail_template = self.env.ref(
                    "auth_signup.set_password_email", raise_if_not_found=False
                )
            except ValueError:
                pass
        if not mail_template:
            mail_template = self.env.ref("auth_signup.reset_password_email")
        assert mail_template._name == "mail.template"

        mail_template_values = {
            "email_to": "${object.email|safe}",
            "email_cc": False,
            "auto_delete": True,
            "partner_to": False,
            "scheduled_date": False,
        }
        mail_template.write(mail_template_values)

        # 消息模板
        message_template = False
        if create_mode:
            try:
                message_template = self.env.ref(
                    "wxwork_auth_oauth.set_password_message", raise_if_not_found=False
                )
            except ValueError:
                pass
        if not message_template:
            message_template = self.env.ref("wxwork_auth_oauth.reset_password_message")
        assert message_template._name == "wxwork.message.template"

        message_template_values = {
            "message_to_user": "${object.wxwork_id|safe}",
            "auto_delete": True,
            "scheduled_date": False,
        }
        message_template.write(message_template_values)

        for user in self:
            if user.notification_type == "wxwork":
                if not user.wxwork_id:
                    raise UserError(
                        _(
                            "Cannot send user %s has no Enterprise WeChat user id.",
                            user.name,
                        )
                    )
                with self.env.cr.savepoint():
                    force_send = not (self.env.context.get("import_file", False))

                    message_template.send_message(
                        user.id, force_send=force_send, raise_exception=True
                    )
                _logger.info(
                    _("Password reset message sent for user: %s, %s"),
                    user.name,
                    user.wxwork_id,
                )
            else:
                if not user.email:
                    raise UserError(
                        _("Cannot send email: user %s has no email address.", user.name)
                    )
                # TDE FIXME: make this template technical (qweb)
                with self.env.cr.savepoint():
                    force_send = not (self.env.context.get("import_file", False))
                    mail_template.send_mail(
                        user.id, force_send=force_send, raise_exception=True
                    )
                _logger.info(
                    "Password reset email sent for user <%s> to <%s>",
                    user.login,
                    user.email,
                )

    def send_unregistered_user_reminder(self, after_days=5):
        """
        发送未注册的用户提醒 消息
        """

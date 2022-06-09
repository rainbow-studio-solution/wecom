# -*- coding: utf-8 -*-

import logging
import json
import requests

from collections import defaultdict
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.addons.base.models.ir_mail_server import MailDeliveryException
from odoo.addons.auth_signup.models.res_partner import SignupError, now

from odoo.exceptions import AccessDenied


_logger = logging.getLogger(__name__)

from odoo.http import request


class ResUsers(models.Model):
    _inherit = "res.users"

    # ---------------------
    # 发送消息
    # ---------------------
    def action_reset_password(self):
        """
        为每个用户创建注册令牌，并通过电子邮件发送他们的注册url
        增加判断模板对象为企业微信用户，使用企业微信发送模板消息的方法
        """
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
        email_values = {
            "email_cc": False,
            # "message_to_user": "${object.wecom_userid|safe}",
            'recipient_ids': [],
            "auto_delete": True,
            "partner_to": False,
            "scheduled_date": False,
        }
        # template.write(template_values)
        for user in self:
            if user.wecom_userid:
                email_values['message_to_user'] = user.wecom_userid
                return self.action_reset_password_by_wecom(user, template)
            elif not user.email:
                raise UserError(
                    _("Cannot send email: user %s has no email address.", user.name)
                )
            email_values['email_to'] = user.email
            # TDE FIXME: make this template technical (qweb)
            with self.env.cr.savepoint():
                force_send = not (self.env.context.get("import_file", False))
                template.send_mail(user.id, force_send=force_send, raise_exception=True)
            _logger.info(
                "Password reset email sent for user <%s> to <%s>",
                user.login,
                user.email,
            )
        return super(ResUsers, self).action_reset_password()

    def action_reset_password_by_wecom(self, user, template):
        """
        通过企业微信的方式发送模板消息
        """
        with self.env.cr.savepoint():
            force_send = not (self.env.context.get("import_file", False))
            template.send_message(
                user.id, force_send=force_send, raise_exception=True,
            )
        _logger.info(
            _("Password reset message sent to user: <%s>,<%s>, <%s>"),
            user.name,
            user.login,
            user.wecom_userid,
        )

    def send_unregistered_user_reminder(self, after_days=5):
        """
        发送未注册的用户提醒 消息
        """
        datetime_min = fields.Datetime.today() - relativedelta(days=after_days)
        datetime_max = datetime_min + relativedelta(hours=23, minutes=59, seconds=59)

        res_users_with_details = self.env["res.users"].search_read(
            [
                ("share", "=", False),
                ("create_uid.email", "!=", False),
                ("create_date", ">=", datetime_min),
                ("create_date", "<=", datetime_max),
                ("log_ids", "=", False),
            ],
            ["create_uid", "name", "login"],
        )

        # 分组邀请
        invited_users = defaultdict(list)
        for user in res_users_with_details:
            invited_users[user.get("create_uid")[0]].append(
                "%s (%s)" % (user.get("name"), user.get("login"))
            )

        # 用于向所有邀请者发送有关其邀请用户的邮件
        for user in invited_users:
            if user.wecom_userid:
                return self.send_unregistered_user_reminder_by_wecom(
                    user, invited_users
                )
            template = self.env.ref(
                "auth_signup.mail_template_data_unregistered_users"
            ).with_context(dbname=self._cr.dbname, invited_users=invited_users[user])
            template.send_mail(
                user, notif_layout="mail.mail_notification_light", force_send=False
            )

    def send_unregistered_user_reminder_by_wecom(self, user, invited_users):
        message_template = self.env.ref(
            "wecom_auth_oauth.message_template_data_unregistered_users"
        ).with_context(dbname=self._cr.dbname, invited_users=invited_users[user])
        message_template.send_message(
            user, notif_layout="mail.mail_notification_light", force_send=False
        )

    @api.model_create_multi
    def create(self, vals_list):
        """
        重写以 发送创建账户的企微消息
        send_message: true 表示发送创建账户的企微消息, false 表示不发送创建账户的企微消息
        批量创建用户时，建议 send_message=False
        """
        users = super(ResUsers, self).create(vals_list)
        if self.env.context.get('send_message'):
            users.send_message_for_new_users()

        return users

    def send_message_for_new_users(self):
        """
        发送创建新用户的企微消息
        """
        template = self.env.ref(
            "auth_signup.mail_template_user_signup_account_created", raise_if_not_found=False
        )
        email_values = {
            "email_cc": False,
            # "message_to_user": "${object.wecom_userid|safe}",
            'recipient_ids': [],
            "auto_delete": True,
            "partner_to": False,
            "scheduled_date": False,
        }
        for user in self:
            email_values['message_to_user'] = user.wecom_userid
            with self.env.cr.savepoint():
                force_send = not (self.env.context.get("import_file", False))
                template.send_message(
                    user.id, force_send=force_send, raise_exception=True,
                )
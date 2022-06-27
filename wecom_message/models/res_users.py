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

    def action_totp_invite(self):
        """
        邀请用户使用 双因素身份验证
        """
        ir_config = self.env["ir.config_parameter"].sudo()
        message_sending_method = ir_config.get_param("wecom.message_sending_method")

        invite_template = self.env.ref("auth_totp_mail.mail_template_totp_invite")
        users_to_invite = self.sudo().filtered(lambda user: not user.totp_secret)
        email_values = {
            "email_from": self.env.user.email_formatted,
            "author_id": self.env.user.partner_id.id,
        }

        if message_sending_method == "1":
            for user in users_to_invite:
                if user.wecom_userid:
                    email_values.update({"message_to_user": user.wecom_userid})
                    self.send_template_email_by_wecom(
                        user,
                        template_name="auth_totp_mail.mail_template_totp_invite",
                        subject=_(
                            "Invitation to activate two-factor authentication on your Odoo account"
                        ),
                        email_values=email_values,
                    )
        else:
            for user in users_to_invite:
                if user.wecom_userid:
                    email_values.update({"message_to_user": user.wecom_userid})
                    self.send_template_email_by_wecom(
                        user,
                        template_name="auth_totp_mail.mail_template_totp_invite",
                        subject=_(
                            "Invitation to activate two-factor authentication on your Odoo account"
                        ),
                        email_values=email_values,
                    )
                invite_template.send_mail(
                    user.id,
                    force_send=True,
                    email_values=email_values,
                    notif_layout="mail.mail_notification_light",
                )

        # Display a confirmation toaster
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "type": "info",
                "sticky": False,
                "message": _(
                    "Invitation to use two-factor authentication sent for the following user(s): %s",
                    ", ".join(users_to_invite.mapped("name")),
                ),
            },
        }

    def action_reset_password(self):
        """
        为每个用户创建注册令牌,并通过电子邮件发送他们的注册url
        增加判断模板对象为企业微信用户,使用企业微信发送模板消息的方法
        """
        ir_config = self.env["ir.config_parameter"].sudo()
        message_sending_method = ir_config.get_param("wecom.message_sending_method")

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
        template_name = ""
        subject = ""
        if create_mode:
            try:
                template = self.env.ref(
                    "auth_signup.set_password_email", raise_if_not_found=False
                )
                subject = _("Invitation")
                template_name = "auth_signup.set_password_email"
            except ValueError:
                pass
        if not template:
            template = self.env.ref("auth_signup.reset_password_email")
            subject = _("Password reset")
            template_name = "auth_signup.reset_password_email"
        assert template._name == "mail.template"
        email_values = {
            "email_cc": False,
            "recipient_ids": [],
            "auto_delete": True,
            "partner_to": False,
            "scheduled_date": False,
        }

        for user in self:
            if user.wecom_userid:
                email_values["message_to_user"] = user.wecom_userid
                email_values.pop("partner_to")
                return self.send_template_email_by_wecom(
                    user, template_name, subject, email_values,
                )
            elif not user.email:
                raise UserError(
                    _("Cannot send email: user %s has no email address.", user.name)
                )
            else:
                if message_sending_method != "1":
                    email_values["email_to"] = user.email
                    # TDE FIXME: make this template technical (qweb)
                    with self.env.cr.savepoint():
                        force_send = not (self.env.context.get("import_file", False))
                        template.send_mail(
                            user.id,
                            force_send=force_send,
                            raise_exception=True,
                            email_values=email_values,
                        )
                    _logger.info(
                        _(
                            "Password reset email sent for user <%s> to <%s>",
                            user.login,
                            user.email,
                        )
                    )

        # return super(ResUsers, self).action_reset_password()

    def send_unregistered_user_reminder(self, after_days=5):
        """
        TODO:发送未注册的用户提醒 消息
        """
        ir_config = self.env["ir.config_parameter"].sudo()
        message_sending_method = ir_config.get_param("wecom.message_sending_method")

        datetime_min = fields.Datetime.today() - relativedelta(days=after_days)
        datetime_max = datetime_min + relativedelta(hours=23, minutes=59, seconds=59)
        print(datetime_min, datetime_max)
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
        print(res_users_with_details)
        # 分组邀请
        invited_users = defaultdict(list)
        for user in res_users_with_details:
            print(user)
            invited_users[user.get("create_uid")[0]].append(
                "%s (%s)" % (user.get("name"), user.get("login"))
            )
        email_values = {
            "email_from": self.env.user.email_formatted,
            "author_id": self.env.user.partner_id.id,
        }
        # 用于向所有邀请者发送有关其邀请用户的邮件
        for user in invited_users:
            if user.wecom_userid:
                email_values.update({"message_to_user": user.wecom_userid})
                self.send_template_email_by_wecom(
                    user,
                    template_name="auth_signup.mail_template_data_unregistered_users",
                    subject=_("Reminder for unregistered users"),
                    email_values=email_values,
                )

            if message_sending_method != "1":
                template = self.env.ref(
                    "auth_signup.mail_template_data_unregistered_users"
                ).with_context(
                    dbname=self._cr.dbname, invited_users=invited_users[user]
                )
                template.send_mail(
                    user, notif_layout="mail.mail_notification_light", force_send=False
                )

    def send_template_email_by_wecom(
        self, user, template_name=False, subject=False, email_values=None,
    ):
        """
        通过企业微信发送模板邮件
        """
        template = self.env.ref(template_name, raise_if_not_found=False)
        notif_layout = False
        with self.env.cr.savepoint():
            template.send_message(
                user.id,
                force_send=True,
                raise_exception=True,
                email_values=email_values,
                notif_layout=False,
            )
        _logger.info("Send [%s] to user [%s]", subject, user.name)

    @api.model_create_multi
    def create(self, vals_list):
        """
        重写以 发送创建账户的企微消息
        send_message: true 表示发送创建账户的企微消息, false 表示不发送创建账户的企微消息
        批量创建用户时，建议 send_message=False
        """
        users = super(ResUsers, self).create(vals_list)

        if self.env.context.get("send_message"):
            email_values = {
                "email_cc": False,
                "recipient_ids": [],
                "auto_delete": True,
                "scheduled_date": False,
            }
            for user in users:
                email_values["message_to_user"] = user.wecom_userid
                self.send_template_email_by_wecom(
                    user,
                    template_name="auth_signup.mail_template_user_signup_account_created",
                    subject=_("Account Created"),
                    email_values=email_values,
                )

        return users


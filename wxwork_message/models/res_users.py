# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = "res.users"

    def action_reset_password(self):
        """ 
        为每个用户创建注册令牌，并通过企业微信消息发送其注册网址 
        """
        # create_mode = bool(self.env.context.get("create_user"))
        # message_template = False
        # if create_mode:
        #     try:
        #         message_template = self.env.ref(
        #             "auth_signup.set_password_email", raise_if_not_found=False
        #         )
        #     except ValueError:
        #         pass
        # if not message_template:
        #     message_template = self.env.ref("wxwork_message.reset_password_email")
        # assert message_template._name == "wxwork.message.template"

        # message_template_values = {
        #     "email_to": "${object.email|safe}",
        #     "email_cc": False,
        #     "auto_delete": True,
        #     "partner_to": False,
        #     "scheduled_date": False,
        # }
        # message_template.write(message_template_values)

        for user in self:
            if user.notification_type == "wxwork":
                if not user.wxwork_id:
                    raise UserError(
                        _(
                            "Cannot send user %s has no Enterprise WeChat user id.",
                            user.name,
                        )
                    )
                else:
                    # with self.env.cr.savepoint():
                    #     force_send = not (self.env.context.get("import_file", False))
                    #     message_template.send_message(
                    #         user.id, force_send=force_send, raise_exception=True
                    #     )
                    _logger.info(
                        _("Password reset message sent for user: %s, %s"),
                        user.name,
                        user.wxwork_id,
                    )

        return super(ResUsers, self).action_reset_password()

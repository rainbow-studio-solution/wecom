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
        # res_id 是用户id
        if self.env["res.users"].browse(res_id).notification_type == "wxwork":
            # 拦截 用户通知类型为企业微信的发送方式
            pass

        return super(MailTemplate, self).send_mail(
            res_id,
            force_send=False,
            raise_exception=False,
            email_values=None,
            notif_layout=False,
        )

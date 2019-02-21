# -*- coding: utf-8 -*-

import logging
from ast import literal_eval
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools.misc import ustr

from odoo.addons.base.models.ir_mail_server import MailDeliveryException
from odoo.addons.auth_signup.models.res_partner import SignupError, now

_logger = logging.getLogger(__name__)

class Users(models.Model):
    _inherit = 'res.users'

    def preference_wxwork_change_password(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'wxwork_change_password',
            'target': 'new',
        }

    @api.multi
    def action_wxwork_reset_password(self):
        """ 为每个企微用户创建注册令牌，并通过企业微信发送重置密码的URL """
        pass

        # template = False
        #
        # if not template:
        # template = self.env.ref('wxwork_reset_password.reset_password_email')
        # assert template._name == 'wxwork.notice.template'
        #
        # template_values = {
        #     'to_user': '${object.wxwork_id|safe}',
        # }
        # template.write(template_values)
        #
        # for user in self:
        #     with self.env.cr.savepoint():
        #         template.with_context(lang=user.lang).send_notice(user.id, force_send=True, raise_exception=True)
        #     _logger.info("密码重置的企业微信通知发送到用户名：<%s> 企业微信ID：<%s>", user.name, user.wxwork_id)
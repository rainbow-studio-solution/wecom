# -*- coding: utf-8 -*-

import json
from odoo import models, fields, api, _
from odoo.exceptions import AccessDenied, UserError
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.exceptions import except_orm, Warning, RedirectWarning,AccessDenied
import odoo.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)

class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def auth_oauth_wxwork(self, provider, validation):
        oauth_uid = validation['UserId']
        oauth_user = self.search([("oauth_uid", "=", oauth_uid), ('oauth_provider_id', '=', provider)])
        if not oauth_user or len(oauth_user) > 1:
            return AccessDenied
        return (self.env.cr.dbname, oauth_user.login, oauth_uid)
        # return oauth_user.login

    @api.model
    def _check_credentials(self, password):
        try:
            return super(ResUsers, self)._check_credentials(password)
        except AccessDenied:
            res = self.sudo().search([('id', '=', self.env.uid), ('oauth_uid', '=', password)])
            if not res:
                raise
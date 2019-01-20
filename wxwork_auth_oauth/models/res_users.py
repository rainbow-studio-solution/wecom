# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import AccessDenied

class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def wxwork_auth_oauth_signin(self, params):
        oauth_uid = params['userid']
        # deviceId = params['DeviceId']
        deviceId = params['DeviceId']
        OpenId = params['OpenId']

        if not OpenId:
            raise AccessDenied("抱歉，您非本企业员工")
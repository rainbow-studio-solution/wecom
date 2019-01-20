# -*- coding: utf-8 -*-


import json
import requests
from ..api.CorpApi import *
from ..api.AbstractApi import *
from ..api.api_errcode import *
from odoo import api, http, SUPERUSER_ID, _
from odoo.http import request
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError


class WxworkOAuthLogin(http.Controller):
    @http.route('/auth_oauth/wxwork', type='http', auth='none')
    def signin(self, **kw):
        code = kw.pop('code', None)
        corpid = request.env['ir.config_parameter'].sudo().get_param('wxwork.corpid')
        secret = request.env['ir.config_parameter'].sudo().get_param('wxwork.auth_secret')
        api = CorpApi(corpid, secret)
        try:
            response = api.httpCall(
                CORP_API_TYPE['GET_USER_INFO_BY_CODE'],
                {
                    'code': code,
                }
            )
        except ApiException as e:
            pass

        if not response['DeviceId']:
            raise UserError(_("抱歉，您非本企业员工"))
        else:
            print(response['UserId'])











# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, _

from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException

_logger = logging.getLogger(__name__)


class Partner(models.Model):
    _inherit = "res.partner"

    

    def get_wecom_openid(self):
        """
        获取企微OpenID
        """
        for partner in self:
            print(partner.company_id)
            try:
                wxapi = self.env["wecom.service_api"].InitServiceApi(
                    partner.company_id.corpid,
                    partner.company_id.contacts_app_id.secret,
                )
                response = wxapi.httpCall(
                    self.env["wecom.service_api_list"].get_server_api_call(
                        "USERID_TO_OPENID"
                    ),
                    {"userid": partner.wecom_userid,},
                )
            except ApiException as ex:
                self.env["wecomapi.tools.action"].ApiExceptionDialog(
                    ex, raise_exception=True
                )
            else:
                partner.wecom_openid = response["openid"]
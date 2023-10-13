# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, Command, _

from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException   # type: ignore

_logger = logging.getLogger(__name__)


class Partner(models.Model):
    _inherit = "res.partner"

    wecom_userid = fields.Char(
        string="WeCom User ID",
        readonly=True,
    )
    wecom_openid = fields.Char(
        string="WeCom OpenID",
        readonly=True,
    )

    is_wecom_user = fields.Boolean(
        "Is WeCom user",
        readonly=True,
    )
    qr_code = fields.Char(
        string="Personal QR code",
        readonly=True,
    )
    wecom_user_order = fields.Char(
        "WeCom User sequence",
        default="0",
        readonly=True,
    )

    def get_wecom_openid(self):
        """
        获取企微OpenID
        """
        for partner in self:
            print(partner.company_id)    # type: ignore
            try:
                wxapi = self.env["wecom.service_api"].InitServiceApi(
                    partner.company_id.corpid,   # type: ignore
                    partner.company_id.contacts_app_id.secret,   # type: ignore
                )
                response = wxapi.httpCall(
                    self.env["wecom.service_api_list"].get_server_api_call(
                        "USERID_TO_OPENID"
                    ),
                    {
                        "userid": partner.wecom_userid,  # type: ignore
                    },
                )
            except ApiException as ex:
                self.env["wecomapi.tools.action"].ApiExceptionDialog(
                    ex, raise_exception=True
                )
            else:
                partner.wecom_openid = response["openid"]    # type: ignore

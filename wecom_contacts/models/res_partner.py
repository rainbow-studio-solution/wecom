# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, Command, _

from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException

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
        help="Personal QR code, Scan can be added as external contact",
        readonly=True,
    )
    wecom_user_order = fields.Char(
        "WeCom User sequence",
        default="0",
        help="The sort value in the department, the default is 0. The number must be the same as the department. The larger the number, the higher the order.The value range is [0, 2^32)",
        readonly=True,
    )

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
                    {
                        "userid": partner.wecom_userid,
                    },
                )
            except ApiException as ex:
                self.env["wecomapi.tools.action"].ApiExceptionDialog(
                    ex, raise_exception=True
                )
            else:
                partner.wecom_openid = response["openid"]

 
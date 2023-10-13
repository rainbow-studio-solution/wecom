# -*- coding: utf-8 -*-


from odoo import models, _
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException    # type: ignore


class User(models.Model):
    _inherit = ["res.users"]

    def get_wecom_openid(self):
        """
        获取企微OpenID
        """
        for user in self:
            try:
                wxapi = self.env["wecom.service_api"].InitServiceApi(
                    user.company_id.corpid,  # type: ignore
                        user.company_id.contacts_app_id.secret,  # type: ignore
                    )
                response = wxapi.httpCall(
                    self.env["wecom.service_api_list"].get_server_api_call(
                        "USERID_TO_OPENID"
                    ),
                    {
                        "userid": user.wecom_userid,     # type: ignore
                    },
                )
            except ApiException as ex:
                self.env["wecomapi.tools.action"].ApiExceptionDialog(
                    ex, raise_exception=True
                )
            else:
                user.wecom_openid = response["openid"]   # type: ignore

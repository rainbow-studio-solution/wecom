# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException
import logging

_logger = logging.getLogger(__name__)

RESPONSE = {}


class UserBindWecom(models.TransientModel):
    _name = "wecom.user_bind_wecom_wizard"
    _description = "Users bind enterprise wechat members"

    name = fields.Char(
        string="Name", required=True, compute="_compute_user", store=True,
    )
    avatar = fields.Char(string="Avatar", compute="_compute_user", store=True,)
    wecom_userid = fields.Char(string="Enterprise wechat user Id", required=True)
    user_id = fields.Many2one(
        "res.users", string="Related User", required=True, readonly=True
    )
    user_name = fields.Char(related="user_id.name", readonly=True)
    company_id = fields.Many2one(related="user_id.company_id", readonly=True)

    @api.depends("company_id", "wecom_userid")
    def _compute_user(self):
        for user in self:
            if user.company_id and user.wecom_userid:
                company = user.company_id
                try:
                    wxapi = self.env["wecom.service_api"].InitServiceApi(
                        company.corpid, company.contacts_app_id.secret
                    )
                    response = wxapi.httpCall(
                        self.env["wecom.service_api_list"].get_server_api_call(
                            "USER_GET"
                        ),
                        {"userid": user.wecom_userid},
                    )
                    global RESPONSE
                    RESPONSE = response
                    user.name = response["name"]
                    user.avatar = response["thumb_avatar"]
                except ApiException as ex:
                    return self.env["wecomapi.tools.action"].ApiExceptionDialog(
                        ex, raise_exception=True
                    )
            else:
                user.name = None
                user.avatar = None

    def bind_wecom_member(self):
        user = (
            self.env["res.users"]
            .sudo()
            .search(
                [
                    ("wecom_userid", "=", self.wecom_userid.lower()),
                    ("is_wecom_user", "=", True),
                    ("company_id", "=", self.company_id.id),
                    "|",
                    ("active", "=", True),
                    ("active", "=", False),
                ],
            )
        )
        if len(user) > 0:
            raise UserError(_("User with ID [%s] already exists") % (self.wecom_userid))
        else:
            self.user_id.write(
                {
                    "is_wecom_user": True,
                    "wecom_userid": RESPONSE["userid"],
                    "name": RESPONSE["name"],
                    "qr_code": RESPONSE["qr_code"],
                    "notification_type": "inbox",
                }
            )
            # print(self.user_id.employee_id)
            # for employee in self.user_id.employee_ids:
            self.user_id.employee_id.write(
                {
                    "is_wecom_user": True,
                    "wecom_userid": RESPONSE["userid"],
                    "name": RESPONSE["name"],
                    "qr_code": RESPONSE["qr_code"],
                }
            )


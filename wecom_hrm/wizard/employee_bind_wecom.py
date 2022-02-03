# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException
import logging

_logger = logging.getLogger(__name__)

RESPONSE = {}


class EmployeeBindWecom(models.TransientModel):
    _name = "wecom.wizard.employee_bind_wecom"
    _description = "Employees bind enterprise wechat members"

    name = fields.Char(
        string="Name", required=True, compute="_compute_user", store=True,
    )
    avatar = fields.Char(string="Avatar", compute="_compute_user", store=True,)
    wecom_userid = fields.Char(string="Enterprise wechat user Id", required=True)
    employee_id = fields.Many2one(
        "hr.employee", string="Related Employee", required=True, readonly=True
    )
    employee_name = fields.Char(related="employee_id.name", readonly=True)
    company_id = fields.Many2one(related="employee_id.company_id", readonly=True)

    @api.depends("company_id", "wecom_userid")
    def _compute_user(self):
        for employee in self:
            if employee.company_id and employee.wecom_userid:
                company = employee.company_id
                try:
                    wxapi = self.env["wecom.service_api"].InitServiceApi(
                        company.corpid, company.contacts_app_id.secret
                    )
                    response = wxapi.httpCall(
                        self.env["wecom.service_api_list"].get_server_api_call(
                            "USER_GET"
                        ),
                        {"userid": employee.wecom_userid},
                    )
                    global RESPONSE
                    RESPONSE = response
                    employee.name = response["name"]
                    employee.avatar = response["thumb_avatar"]
                except ApiException as ex:
                    return self.env["wecomapi.tools.action"].ApiExceptionDialog(
                        ex, raise_exception=True
                    )
            else:
                employee.name = None
                employee.avatar = None

    def bind_wecom_member(self):
        # if self.name is None:
        #     raise UserError(
        #         _("There is no member with ID [%s] in enterprise wechat")
        #         % (self.wecom_userid)
        #     )
        employee = (
            self.env["hr.employee"]
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
        if len(employee) > 0:
            raise UserError(
                _("Employee with ID [%s] already exists") % (self.wecom_userid)
            )
        else:
            self.employee_id.write(
                {
                    "is_wecom_user": True,
                    "wecom_userid": RESPONSE["userid"],
                    "name": RESPONSE["name"],
                    "qr_code": RESPONSE["qr_code"],
                }
            )
            if self.employee_id.user_id:
                # 关联了User
                self.employee_id.user_id.write(
                    {
                        "is_wecom_user": True,
                        "wecom_userid": RESPONSE["userid"],
                        "name": RESPONSE["name"],
                        "notification_type": "inbox",
                        "qr_code": RESPONSE["qr_code"],
                    }
                )
                # self.employee_id._sync_user(
                #     self.env["res.users"].sudo().browse(self.employee_id.user_id),
                #     bool(self.employee_id.image_1920),
                # )


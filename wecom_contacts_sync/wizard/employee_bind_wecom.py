# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException
import logging

_logger = logging.getLogger(__name__)

RESPONSE = {}


class EmployeeBindWecom(models.TransientModel):
    _name = "wecom.employee_bind_wecom_wizard"
    _description = "Employees bind enterprise wechat members"

    
    employee_id = fields.Many2one(
        "hr.employee", string="Related Employee", required=True, readonly=True
    )
    # employee_name = fields.Char(related="employee_id.name", readonly=True, store=True,)
    company_id = fields.Many2one(related="employee_id.company_id", readonly=True)

    wecom_user = fields.Many2one("wecom.user",string="Enterprise wechat user", required=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    name = fields.Char(
        string="Name", required=True, compute="_compute_user", store=True,
    )
    avatar = fields.Char(string="Avatar", compute="_compute_user", store=True,)
    

    @api.depends("wecom_user")
    def _compute_user(self):
        for employee in self:
            employee.name = employee.wecom_user.name
            employee.avatar = employee.wecom_user.thumb_avatar

    def bind_wecom_member(self):
        employee = (
            self.env["hr.employee"]
            .sudo()
            .search(
                [
                    ("wecom_user", "=", self.wecom_user.id),
                    ("is_wecom_user", "=", True),
                    ("company_id", "=", self.company_id.id),
                    "|",
                    ("active", "=", True),
                    ("active", "=", False),
                ],
            )
        )
        if employee:
            raise UserError(
                _("Employee with ID [%s] already exists") % (self.wecom_user)
            )
        else:
            self.employee_id.write(
                {
                    "is_wecom_user": True,
                    "wecom_user": self.wecom_user.id,
                }
            )
            if self.employee_id.user_id:
                # 关联了User
                self.employee_id.user_id.write(
                    {
                        "is_wecom_user": True,
                        "wecom_user": self.wecom_user.id,
                        # "name": RESPONSE["name"],
                        # "notification_type": "inbox",
                        # "qr_code": RESPONSE["qr_code"],
                    }
                )
                # self.employee_id._sync_user(
                #     self.env["res.users"].sudo().browse(self.employee_id.user_id),
                #     bool(self.employee_id.image_1920),
                # )


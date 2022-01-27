# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException
import logging

_logger = logging.getLogger(__name__)


class EmployeeBindWecom(models.TransientModel):
    _name = "wecom.wizard.employee_bind_wecom"
    _description = "Employees bind enterprise wechat members"

    name = fields.Char(
        string="Name",
        required=True,
        compute="_compute_name",
        store=True,
    )
    wecom_userid = fields.Char(string="Enterprise wechat user Id", required=True)
    employee_id = fields.Many2one(
        "hr.employee", string="Related Employee", required=True, readonly=True
    )
    employee_name = fields.Char(related="employee_id.name", readonly=True)
    company_id = fields.Many2one(related="employee_id.company_id", readonly=True)

    @api.depends("company_id", "wecom_userid")
    def _compute_name(self):
        pass

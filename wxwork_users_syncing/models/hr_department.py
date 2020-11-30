# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import time
import logging

from ...wxwork_api.wx_qy_api.CorpApi import *


_logger = logging.getLogger(__name__)


class HrDepartment(models.Model):
    _inherit = "hr.department"
    _description = "Enterprise WeChat Department"
    _order = "wxwork_department_id"

    wxwork_department_id = fields.Many2one(
        "hr.employee",
        string="Enterprise WeChat department ID",
        default=1,
        help="Enterprise WeChat department ID",
        readonly=True,
        translate=True,
        index=True,
    )
    wxwork_department_parent_id = fields.Integer(
        "Enterprise WeChat parent department ID",
        default=1,
        help="Parent department ID,32-bit integer.Root department is 1",
        readonly=True,
        translate=True,
    )
    wxwork_department_order = fields.Char(
        "Enterprise WeChat department sort",
        default="1",
        help="Order value in parent department. The higher order value is sorted first. The value range is[0, 2^32)",
        readonly=True,
        translate=True,
    )
    is_wxwork_department = fields.Boolean(
        "Enterprise WeChat Department", readonly=True, translate=True
    )

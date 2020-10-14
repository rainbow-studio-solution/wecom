# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

from ...wxwork_api.wx_qy_api.CorpApi import *
from ...wxwork_api.helper.common import *

# 代码分析
from odoo.tools.misc import profile

import logging
import platform
import time

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = "hr.employee"
    _description = "Enterprise WeChat employees"
    _order = "wxwork_user_order"

    wxwork_id = fields.Char(
        string="Enterprise WeChat user Id", readonly=True, translate=True
    )
    alias = fields.Char(string="Alias", readonly=True, translate=True)
    department_ids = fields.Many2many(
        "hr.department",
        "wxwork_department_id",
        string="Enterprise WeChat multi-department",
        readonly=True,
        translate=True,
    )
    qr_code = fields.Binary(
        string="Personal QR code",
        help="Personal QR code, Scan can be added as external contact",
        readonly=True,
        translate=True,
    )
    wxwork_user_order = fields.Char(
        "Enterprise WeChat user sort",
        default="0",
        help="The sort value within the department, the default is 0. The quantity must be the same as the department, The greater the value the more sort front.The value range is [0, 2^32)",
        readonly=True,
    )
    is_wxwork_employee = fields.Boolean(
        string="Enterprise WeChat employees", readonly=True, default=False,
    )

    user_check_tick = fields.Boolean(string="User Check Tick", default=False,)


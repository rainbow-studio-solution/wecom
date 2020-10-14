# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.exceptions import UserError

# from ..models.sync_user import *

# from ..models.hr_employee import EmployeeSyncUser
import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _name = "wizard.wxwork.user"
    _description = "Enterprise WeChat Generation System User Guide"
    _order = "create_date"

    sync_user_result = fields.Boolean(
        string="User synchronization result", default=False, readonly=True
    )
    times = fields.Float(string="Elapsed time (seconds)", digits=(16, 3), readonly=True)
    result = fields.Text(string="Result", readonly=True)


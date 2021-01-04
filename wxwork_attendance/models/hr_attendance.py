# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _


class HrAttendance(models.Model):
    _inherit = "hr.attendance"
    _description = "Enterprise WeChat Attendance Record"

    check_in_exception = fields.Boolean(
        string="Abnormal clocking in at work", readonly=True
    )
    check_out_exception = fields.Boolean(
        string="Check in abnormal after get off work", readonly=True
    )

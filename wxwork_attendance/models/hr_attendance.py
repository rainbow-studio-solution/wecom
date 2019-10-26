# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _


class HrAttendance(models.Model):
    _inherit = "hr.attendance"
    _description = '企业微信打卡'


    check_in_exception = fields.Boolean(string="上班打卡异常", readonly=True)
    check_out_exception = fields.Boolean(string="下班打卡异常", readonly=True)

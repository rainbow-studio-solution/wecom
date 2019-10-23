# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _


class HrAttendance(models.Model):
    _inherit = "hr.attendance"
    _description = '企业微信打卡'

    groupname = fields.Char(string='打卡规则名称', readonly=True)
    checkin_type = fields.Selection(
        ([('1', '上下班打卡'),('2', '外出打卡'),('3', '全部打卡')]),
        string='打卡类型', readonly=True)

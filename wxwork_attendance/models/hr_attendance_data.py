# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _


class HrAttendanceWxwrokData(models.Model):
    _name = "hr.attendance.wxwrok.data"
    _description = "Enterprise WeChat attendance data"

    name = fields.Char(string="Name", readonly=True)
    wxwork_id = fields.Char(string="Enterprise WeChat user ID", readonly=True)
    groupname = fields.Char(string="Attendance rule name", readonly=True)
    # checkin_type = fields.Selection(
    #     ([('1', '上下班打卡'), ('2', '外出打卡'), ('3', '全部打卡')]),
    #     string='打卡类型', readonly=True)
    checkin_type = fields.Char(string="Attendance type", readonly=True)
    exception_type = fields.Char(string="Abnormal", readonly=True)
    checkin_time = fields.Datetime(string="Check-in time", readonly=True)
    location_title = fields.Char(string="Check-in location", readonly=True)
    location_detail = fields.Char(string="Check-in location details", readonly=True)
    wifiname = fields.Char(string="Check-in wifi name", readonly=True)
    notes = fields.Char(string="Check-in notes", readonly=True)
    wifimac = fields.Char(string="Check-in MMAC address/bssid", readonly=True)
    mediaids = fields.Char(string="Check-in Attachment media_id", readonly=True)
    lat = fields.Char(string="Check-in Latitude of location", readonly=True)
    lng = fields.Char(string="Check-in longitude of location", readonly=True)


# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _


class HrAttendanceWxwrokData(models.Model):
    _name = "hr.attendance.wxwrok.data"
    _description = "Enterprise WeChat attendance data"
    _order = "checkin_time"

    name = fields.Char(string="Name", readonly=True,)
    userid = fields.Char(string="Enterprise WeChat user ID", readonly=True)
    groupname = fields.Char(string="Attendance rule name", readonly=True)
    # checkin_type = fields.Selection(
    #     ([("1", "上班打卡"), ("2", "下班打卡"), ("3", "外出打卡")]),
    #     string="打卡类型",
    #     readonly=True,
    #     help="打卡类型。字符串，目前有：上班打卡，下班打卡，外出打卡",
    # )

    checkin_type = fields.Char(
        string="Clock type", readonly=True, help="打卡类型。字符串，目前有：上班打卡，下班打卡，外出打卡"
    )
    exception_type = fields.Char(
        string="Exception type",
        readonly=True,
        help="异常类型，字符串，包括：时间异常，地点异常，未打卡，wifi异常，非常用设备。如果有多个异常，以分号间隔",
    )
    checkin_time = fields.Date(
        string="Check-in time", readonly=True, help="打卡时间。Unix时间戳"
    )
    location_title = fields.Char(
        string="Check-in location", readonly=True, help="打卡地点title"
    )
    location_detail = fields.Char(
        string="Check-in location details", readonly=True, help="打卡地点详情"
    )
    wifiname = fields.Char(string="Check-in wifi name", readonly=True, help="打卡wifi名称")
    notes = fields.Char(string="Check-in notes", readonly=True, help="打卡备注")
    wifimac = fields.Char(
        string="Check-in MMAC address/bssid", readonly=True, help="打卡的MAC地址/bssid"
    )
    mediaids = fields.Char(
        string="Check-in Attachment media id",
        readonly=True,
        help="打卡的附件media_id，可使用media/get获取附件",
    )
    lat = fields.Integer(
        string="Check-in Latitude of location",
        readonly=True,
        help="位置打卡地点纬度，是实际纬度的1000000倍，与腾讯地图一致采用GCJ-02坐标系统标准",
    )
    lng = fields.Integer(
        string="Check-in longitude of location",
        readonly=True,
        help="位置打卡地点经度，是实际经度的1000000倍，与腾讯地图一致采用GCJ-02坐标系统标准",
    )
    deviceid = fields.Char(string="", readonly=True, help="打卡设备id",)
    sch_checkin_time = fields.Date(
        string="Standard punch time",
        readonly=True,
        help="标准打卡时间，指此次打卡时间对应的标准上班时间或标准下班时间",
    )
    groupid = fields.Integer(
        string="Attendance rule Id", readonly=True, help="规则id，表示打卡记录所属规则的id",
    )
    schedule_id = fields.Integer(
        string="Shift id", readonly=True, help="班次id，表示打卡记录所属规则中，所属班次的id",
    )
    timeline_id = fields.Integer(
        string="Time line id",
        readonly=True,
        help="时段id，表示打卡记录所属规则中，某一班次中的某一时段的id，如上下班时间为9:00-12:00、13:00-18:00的班次中，9:00-12:00为其中一组时段",
    )


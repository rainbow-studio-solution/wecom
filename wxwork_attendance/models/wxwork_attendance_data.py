# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

class HrWxworkAttendanceData(models.Model):
    _name = "hr.attendance.data.wxwrok"
    _description = '企业微信打卡数据'

    name = fields.Char(string="姓名", readonly=True)
    wxwork_id = fields.Char(string='企微用户Id', readonly=True)
    groupname = fields.Char(string='打卡规则名称', readonly=True)
    # checkin_type = fields.Selection(
    #     ([('1', '上下班打卡'), ('2', '外出打卡'), ('3', '全部打卡')]),
    #     string='打卡类型', readonly=True)
    checkin_type = fields.Char(string='打卡类型', readonly=True)
    exception_type = fields.Char(string='异常', readonly=True)
    checkin_time = fields.Datetime(string='企微打卡时间', readonly=True)
    location_title = fields.Char(string='打卡地点标题', readonly=True)
    location_detail = fields.Char(string='打卡地点详情', readonly=True)
    wifiname = fields.Char(string='打卡wifi名称', readonly=True)
    notes = fields.Char(string='打卡备注', readonly=True)
    wifimac = fields.Char(string='打卡的MAC地址/bssid', readonly=True)
    mediaids = fields.Char(string='打卡的附件media_id', readonly=True)
    lat = fields.Char(string='打卡地点纬度', readonly=True)
    lng = fields.Char(string='打卡地点经度', readonly=True)


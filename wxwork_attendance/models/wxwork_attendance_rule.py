# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

class HrWxworkAttendanceData(models.Model):
    _name = "hr.attendance.rule.wxwrok"
    _description = '企业微信打卡数据'

    groupid = fields.Char(string='打卡规则id', readonly=True)
    name = fields.Char(string="打卡规则名称", readonly=True)#groupname
    wxwork_id = fields.Char(string='企微用户Id', readonly=True)#userid
    grouptype = fields.Char(string='打卡规则类型', readonly=True, help='1：固定时间上下班；2：按班次上下班；3：自由上下班')
    checkindate = fields.Datetime(string='打卡时间', readonly=True)
    workdays = fields.Datetime(string='工作日', readonly=True, help="为固定时间上下班或自由上下班，则1到6分别表示星期一到星期六，0表示星期日；若为按班次上下班，则表示拉取班次的日期。")
    work_sec = fields.Datetime(string='上班时间', readonly=True, help="表示为距离当天0点的秒数")
    off_work_sec = fields.Datetime(string='下班时间', readonly=True, help="表示为距离当天0点的秒数")
    remind_work_sec = fields.Datetime(string='上班提醒时间', readonly=True, help="表示为距离当天0点的秒数")
    remind_off_work_sec = fields.Datetime(string='下班提醒时间', readonly=True, help="表示为距离当天0点的秒数")
    flex_time = fields.Datetime(string='弹性时间', readonly=True, help="弹性时间（毫秒）")
    noneed_offwork = fields.Datetime(string='下班不需要打卡', readonly=True, )
    limit_aheadtime = fields.Datetime(string='打卡时间限制', readonly=True, help="打卡时间限制（毫秒）" )
    spe_workdays = fields.Datetime(string='特殊日期', readonly=True, help="" )
    timestamp = fields.Datetime(string='特殊日期具体时间', readonly=True, help="" )
    notes = fields.Datetime(string="特殊日期备注", readonly=True, help="" )
    allow_checkin_offworkday = fields.Datetime(string="是否非工作日允许打卡", readonly=True, help="" )
    sync_holidays = fields.Datetime(string="是否同步法定节假日", readonly=True, help="" )
    need_photo = fields.Datetime(string="是否打卡必须拍照", readonly=True, help="" )
    note_can_use_local_pic = fields.Datetime(string="是否备注时允许上传本地图片", readonly=True, help="" )
    allow_apply_offworkday = fields.Datetime(string="是否允许异常打卡时提交申请", readonly=True, help="" )
    wifimac_infos = fields.Datetime(string="WiFi打卡地点信息", readonly=True, help="" )
    wifiname = fields.Datetime(string="WiFi打卡地点名称", readonly=True, help="" )
    wifimac = fields.Datetime(string="WiFi打卡地点MAC地址/bssid", readonly=True, help="" )
    loc_infos = fields.Datetime(string="位置打卡地点信息", readonly=True, help="" )
    lat = fields.Datetime(string="位置打卡地点纬度", readonly=True, help="是实际纬度的1000000倍，与腾讯地图一致采用GCJ-02坐标系统标准" )
    lng = fields.Datetime(string="位置打卡地点经度", readonly=True, help="是实际经度的1000000倍，与腾讯地图一致采用GCJ-02坐标系统标准" )
    loc_title = fields.Datetime(string="位置打卡地点名称", readonly=True, help="" )
    loc_detail = fields.Datetime(string="位置打卡地点详情", readonly=True, help="" )
    distance = fields.Datetime(string="允许打卡范围（米）", readonly=True, help="" )


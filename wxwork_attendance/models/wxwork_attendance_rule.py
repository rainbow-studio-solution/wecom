# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
import datetime

class HrWxworkAttendanceData(models.Model):
    _name = "hr.attendance.rule.wxwrok"
    _description = '企业微信打卡数据'

    name = fields.Char(string="姓名", readonly=True)
    groupid = fields.Char(string='打卡规则id', readonly=True)
    groupname = fields.Char(string="打卡规则名称", readonly=True)#groupname
    wxwork_id = fields.Char(string='企微用户Id', readonly=True)#userid
    pull_time = fields.Datetime(string='拉取日期', readonly=True, help="日期当天0点", )#compute='_compute_time'

    grouptype = fields.Char(string='打卡规则类型', readonly=True, help='1：固定时间上下班；2：按班次上下班；3：自由上下班')

    checkindate_json = fields.Char(string='打卡时间JSON', readonly=True)

    spe_workdays_json = fields.Char(string='特殊日期JSON', readonly=True, help="" )

    spe_offdays_json = fields.Char(string='不需要打卡的日期JSON', readonly=True, help="" )

    allow_checkin_offworkday = fields.Char(string="是否非工作日允许打卡", readonly=True, help="" )
    sync_holidays = fields.Char(string="是否同步法定节假日", readonly=True, help="" )
    need_photo = fields.Char(string="是否打卡必须拍照", readonly=True, help="" )
    note_can_use_local_pic = fields.Char(string="是否备注时允许上传本地图片", readonly=True, help="" )
    allow_apply_offworkday = fields.Char(string="是否允许异常打卡时提交申请", readonly=True, help="" )

    wifimac_infos = fields.Char(string="WiFi打卡地点信息", readonly=True, help="" )

    loc_infos = fields.Char(string="位置打卡地点信息", readonly=True, help="" )




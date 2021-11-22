# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _


class HrAttendanceWxwrokRule(models.Model):
    _name = "hr.attendance.wxwrok.rule"
    _description = "Enterprise WeChat attendance rule"
    _order = "create_time"

    name = fields.Char(string="Attendance rule name", readonly=True, help="打卡规则名称",)
    groupid = fields.Integer(string="Attendance rule id", readonly=True, help="打卡规则id",)
    groupname = fields.Char(
        string="Attendance rule name", readonly=True, help="打卡规则名称",
    )
    grouptype = fields.Selection(
        [("1", _("Fixed time")), ("2", _("By shift")), ("3", _("Freedom")),],
        string="Attendance rule type",
        readonly=True,
        help="打卡规则类型，1：固定时间上下班；2：按班次上下班；3：自由上下班",
    )
    checkindate = fields.Char(
        string="Attendance time data", readonly=True, help="打卡时间，当规则类型为排班时没有意义",
    )
    spe_workdays = fields.Char(
        string="Special date - must check in date information",
        readonly=True,
        help="特殊日期-必须打卡日期信息，timestamp表示具体时间",
    )
    spe_offdays = fields.Char(
        string="Special date-no check-in date information",
        readonly=True,
        help="特殊日期-不用打卡日期信息， timestamp表示具体时间",
    )
    sync_holidays = fields.Boolean(
        string="Synchronize statutory holidays",
        readonly=True,
        help="是否同步法定节假日，true为同步，false为不同步，当前排班不支持",
    )
    need_photo = fields.Boolean(
        string="Must take pictures",
        readonly=True,
        help="字段：group.spe_offdays.need_photo,是否打卡必须拍照，true为必须拍照，false为不必须拍照",
    )
    note_can_use_local_pic = fields.Boolean(
        string="Allow local images to be uploaded when remarks",
        readonly=True,
        help="是否备注时允许上传本地图片，true为允许，false为不允许",
    )
    allow_checkin_offworkday = fields.Boolean(
        string="Check in on non-working days",
        readonly=True,
        help="是否非工作日允许打卡,true为允许，false为不允许",
    )
    allow_apply_offworkday = fields.Boolean(
        string="Allow to submit card replacement application",
        readonly=True,
        help="是否允许提交补卡申请，true为允许，false为不允许",
    )
    wifimac_infos = fields.Char(
        string="WiFi check-ins", readonly=True, help="打卡地点-WiFi打卡信息",
    )
    loc_infos = fields.Char(string="WiFi check-ins", readonly=True, help="打卡地点-位置打卡信息",)
    range = fields.Char(
        string="Check-in staff information", readonly=True, help="打卡人员信息",
    )
    create_time = fields.Date(
        string="UTC creation time", readonly=True, help="创建打卡规则时间，为unix时间戳",
    )
    white_users = fields.Char(
        string="Whitelist", readonly=True, help="打卡人员白名单，即不需要打卡人员，需要有设置白名单才能查看"
    )
    type = fields.Selection(
        [
            ("0", _("Mobile phone")),
            ("2", _("Attendance machine")),
            ("3", _("Mobile phone + attendance machine")),
        ],
        string="Check-in method",
        readonly=True,
        help="打卡方式，0:手机；2:智慧考勤机；3:手机+智慧考勤机",
    )
    reporterinfo = fields.Char(string="Report to", readonly=True, help="汇报对象信息")
    ot_info = fields.Char(
        string="Overtime information", readonly=True, help="加班信息，相关信息需要设置后才能显示"
    )
    allow_apply_bk_cnt = fields.Integer(
        string="Maximum number of card replacements",
        readonly=True,
        help="每月最多补卡次数，默认-1表示不限制",
    )
    option_out_range = fields.Selection(
        [
            ("0", _("Out of range exception")),
            ("1", _("Normal field work")),
            ("2", _("No punching out of range")),
        ],
        string="Out-of-range punch card processing",
        readonly=True,
        help="范围外打卡处理方式，0-视为范围外异常，默认值；1-视为正常外勤；2:不允许范围外打卡",
    )
    create_userid = fields.Char(string="Created by", readonly=True, help="规则创建人userid")
    use_face_detect = fields.Boolean(
        string="Face recognition attendance switch",
        readonly=True,
        help="人脸识别打卡开关，true为启用，false为不启用",
    )
    allow_apply_bk_day_limit = fields.Integer(
        string="Time limit for card replacement",
        readonly=True,
        help="允许补卡时限，默认-1表示不限制。单位天",
    )
    update_userid = fields.Char(
        string="Last modified by", readonly=True, help="规则最近编辑人userid"
    )
    schedulelist = fields.Char(
        string="Scheduling information", readonly=True, help="排班信息，只有规则为按班次上下班打卡时才有该配置",
    )
    offwork_interval_time = fields.Integer(
        string="Free sign in", readonly=True, help="自由签到，上班打卡后xx秒可打下班卡",
    )

    # @api.model
    # def create(self, values):
    #     values["grouptype"] = "1"
    #     line = super(HrAttendanceWxwrokRule, self).create(values)
    #     return line

    # @api.multi
    # def write(self, vals):
    #     vals["grouptype"] = "1"
    #     ret = super(HrAttendanceWxwrokRule, self).write(vals)


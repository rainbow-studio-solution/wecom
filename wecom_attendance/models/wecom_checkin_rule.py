# -*- coding: utf-8 -*-

import datetime
import time
import json
import binascii

import logging
from odoo import models, fields, api, exceptions, _
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException

_logger = logging.getLogger(__name__)


class WecomCheckinRule(models.Model):
    """
    打卡规则
    """

    _name = "wecom.checkin.rule"
    _description = "Wecom Checkin Rules"
    _order = "create_time"

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        domain="[('is_wecom_organization', '=', True)]",
        copy=False,
        store=True,
    )

    group = fields.Text(
        string="Information about Checkin rules", readonly=True,
    )  # 打卡规则相关信息
    name = fields.Char(string="Name", readonly=True,)  # 打卡规则信息

    grouptype = fields.Integer(
        string="Checkin rule type", readonly=True
    )  # 打卡规则类型。1：固定时间上下班；2：按班次上下班；3：自由上下班 。
    groupname = fields.Char(string="Checkin rule id", readonly=True,)  # 卡规则名称
    groupid = fields.Integer(string="Checkin rule id", readonly=True,)  # 打卡规则id
    checkindate = fields.Text(
        string="Checkin time data", readonly=True,
    )  # 打卡时间配置，当规则类型为排班时没有意义
    spe_workdays = fields.Text(
        string="Special date - must check in date information", readonly=True,
    )  # 特殊日期-必须打卡日期信息，timestamp表示具体时间
    spe_offdays = fields.Text(
        string="Special date-no check-in date information", readonly=True,
    )  # 特殊日期-不用打卡日期信息， timestamp表示具体时间
    sync_holidays = fields.Boolean(
        string="Synchronize statutory holidays", readonly=True, help="",
    )  # 是否同步法定节假日，true为同步，false为不同步，当前排班不支持
    need_photo = fields.Boolean(
        string="Must take pictures", readonly=True,
    )  # 字段：group.spe_offdays.need_photo,是否打卡必须拍照，true为必须拍照，false为不必须拍照
    wifimac_infos = fields.Text(
        string="WiFi check-ins", readonly=True,
    )  # 打卡地点-WiFi打卡信息
    note_can_use_local_pic = fields.Boolean(
        string="Allow local images to be uploaded when remarks", readonly=True,
    )  # 是否备注时允许上传本地图片，true为允许，false为不允许
    allow_checkin_offworkday = fields.Boolean(
        string="Check in on non-working days", readonly=True,
    )  # 是否非工作日允许打卡,true为允许，false为不允许
    allow_apply_offworkday = fields.Boolean(
        string="Allow to submit card replacement application", readonly=True,
    )  # 是否允许提交补卡申请，true为允许，false为不允许
    loc_infos = fields.Text(string="WiFi check-ins", readonly=True,)  # 打卡地点-位置打卡信息
    range = fields.Text(string="Check-in staff information", readonly=True,)  # 打卡人员信息
    create_time = fields.Date(
        string="UTC creation time", readonly=True,
    )  # 创建打卡规则时间，为unix时间戳
    white_users = fields.Text(
        string="Whitelist", readonly=True
    )  # 打卡人员白名单，即不需要打卡人员，需要有设置白名单才能查看
    type = fields.Integer(
        string="Checkin type", readonly=True
    )  # 打卡方式，0:手机；2:智慧考勤机；3:手机+智慧考勤机
    reporterinfo = fields.Text(string="Report to", readonly=True)  # 汇报对象信息
    ot_info = fields.Text(
        string="Overtime information", readonly=True,
    )  # 加班信息，相关信息需要设置后才能显示
    allow_apply_bk_cnt = fields.Integer(
        string="Maximum number of card replacements", readonly=True,
    )  # 每月最多补卡次数，默认-1表示不限制
    option_out_range = fields.Integer(
        string="Out-of-range punch card processing", readonly=True,
    )  # 范围外打卡处理方式，0-视为范围外异常，默认值；1-视为正常外勤；2:不允许范围外打卡
    create_userid = fields.Char(string="Created by", readonly=True)  # 规则创建人userid
    use_face_detect = fields.Boolean(
        string="Face recognition attendance switch", readonly=True,
    )  # 人脸识别打卡开关，true为启用，false为不启用
    allow_apply_bk_day_limit = fields.Integer(
        string="Time limit for card replacement", readonly=True,
    )  # 允许补卡时限，默认-1表示不限制。单位天
    update_userid = fields.Char(
        string="Last modified by", readonly=True
    )  # 规则最近编辑人userid
    schedulelist = fields.Text(
        string="Scheduling information", readonly=True,
    )  # 排班信息，只有规则为按班次上下班打卡时才有该配置
    offwork_interval_time = fields.Integer(
        string="Free sign in", readonly=True,
    )  # 自由签到，上班打卡后xx秒可打下班卡

    @api.model
    def get_checkin_rules(self):
        """
        获取企微打卡规则
        """
        try:
            wxapi = self.env["wecom.service_api"].InitServiceApi(
                self.company_id.corpid, self.company_id.material_app_id.secret,
            )
        except ApiException as ex:
            return self.env["wecomapi.tools.action"].ApiExceptionDialog(
                ex, raise_exception=True
            )

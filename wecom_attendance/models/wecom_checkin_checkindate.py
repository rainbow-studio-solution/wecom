# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _


class WecomCheckinCheckindate(models.Model):
    """
    打卡日期时间,当规则类型为排班时没有意义
    """

    _name = "wecom.checkin.checkindate"
    _description = "Wecom Check-in date"

    rule_id = fields.Many2one("wecom.checkin.rule")  # 打卡规则id
    name = fields.Char(string="Name", related="rule_id.name",)  # 打卡规则名称

    workdays = fields.Text(
        string="workdays", readonly=True,default="{}"
    ) # 工作日。若为固定时间上下班或自由上下班，则1到6分别表示星期一到星期六，0表示星期日
    checkintime = fields.Text(
        string="Check-in time information", readonly=True,default="{}"
    ) # 工作日上下班打卡时间信息，在打卡时间面板中进行设置

    noneed_offwork = fields.Boolean(string="No need to Check-out after work")  # 下班不需要打卡，true为下班不需要打卡，false为下班需要打卡
    limit_aheadtime = fields.Integer(string="Check-in time limit")  # 打卡时间限制（毫秒）
    flex_on_duty_time = fields.Integer(string="Late times are allowed")  # 允许迟到时间，单位ms
    flex_off_duty_time = fields.Integer(string="Early departure time allowed")  # 允许早退时间，单位ms


    # 工作日。若为固定时间上下班或自由上下班，则1到6分别表示星期一到星期六，0表示星期日
    workdays_0 = fields.Boolean(string="Sunday")  # 星期日
    workdays_1 = fields.Boolean(string="Monday")  # 星期一
    workdays_2 = fields.Boolean(string="Tuesday")  # 星期二
    workdays_3 = fields.Boolean(string="Wednesday")  # 星期三
    workdays_4 = fields.Boolean(string="Thursday")  # 星期四
    workdays_5 = fields.Boolean(string="Friday")  # 星期五
    workdays_6 = fields.Boolean(string="Saturday")  # 星期六
    

    def create_or_update_checkindate(self):
        """
        创建或更新 打卡日期时间
        """
        
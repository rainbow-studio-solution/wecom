# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _


class WecomCheckinWorkdays(models.Model):
    """
    打卡规则-工作日
    """

    _name = "wecom.checkin.workdays"
    _description = "Wecom attendance workdays"

    rule_id = fields.Many2one("wecom.checkin.rule")  # 打卡规则id
    name = fields.Char(string="Workday name", related="rule_id.name",)  # 打卡规则名称

    monday = fields.Boolean(string="Monday")  # 星期一
    tuesday = fields.Boolean(string="Tuesday")  # 星期二
    wednesday = fields.Boolean(string="Wednesday")  # 星期三
    thursday = fields.Boolean(string="Thursday")  # 星期四
    friday = fields.Boolean(string="Friday")  # 星期五
    saturday = fields.Boolean(string="Saturday")  # 星期六
    sunday = fields.Boolean(string="Sunday")  # 星期日


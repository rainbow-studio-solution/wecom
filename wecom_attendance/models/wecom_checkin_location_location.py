# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _


class WecomCheckinLocationLocation(models.Model):
    """
    打卡地点-WiFi
    """

    _name = "wecom.checkin.location.location"
    _description = "Wecom Check-in Location"

    rule_id = fields.Many2one("wecom.checkin.rule")  # 打卡规则id
    name = fields.Char(string="Name", readonly=True, compute="_compute_name")
    lat = fields.Float(string="Latitude",)  # 纬度
    lng = fields.Float(string="Longitude",)  # 经度
    loc_title = fields.Char(string="Location Title",)  # 地点名称
    loc_detail = fields.Char(string="Location Detail",)  # 地点详情
    distance = fields.Integer(string="Distance",)  # 距离(米)

    @api.depends("loc_title")
    def _compute_name(self):
        for location in self:
            location.name = location.loc_title

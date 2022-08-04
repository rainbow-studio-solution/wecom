# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _


class WecomCheckinLocationWiFi(models.Model):
    """
    打卡地点-WiFi
    """

    _name = "wecom.checkin.location.wifi"
    _description = "Wecom Check-in Location WiFi"

    rule_id = fields.Many2one("wecom.checkin.rule")  # 打卡规则id
    name = fields.Char(string="Name", readonly=True, compute="_compute_name")
    wifiname = fields.Char(string="WiFi Name",)  # 纬度
    wifimac = fields.Char(string="WiFi MAC address",)  # 经度

    @api.depends("wifiname")
    def _compute_name(self):
        for location in self:
            location.name = location.wifiname


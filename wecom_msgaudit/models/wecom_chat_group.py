# -*- coding: utf-8 -*-

import logging
from odoo import _, api, fields, models, tools

_logger = logging.getLogger(__name__)

class WeComChatGroup(models.Model):
    _name = "wecom.chat.group"
    _description = "Wecom Chat Group"

    name = fields.Char(string="Name", compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    roomid = fields.Char(string="Group chat ID")
    room_name = fields.Char(string="Group chat name")
    room_creator = fields.Char(string="Group chat creator")
    room_create_time = fields.Datetime(string="Group chat create time")
    room_notice = fields.Text(string="Group chat notice")
    room_members = fields.Text(string="Group chat members")

    @api.depends('room_name', 'roomid',)
    def _compute_name(self):
        for record in self:
            if record.room_name:
                record.name = record.room_name
            else:
                record.name = record.roomid
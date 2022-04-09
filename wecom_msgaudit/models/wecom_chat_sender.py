# -*- coding: utf-8 -*-

import logging
from odoo import _, api, fields, models, tools

_logger = logging.getLogger(__name__)

class WeComChatSender(models.Model):
    _name = "wecom.chat.sender"
    _description = "Wecom Chat Sender"

    name = fields.Char(string="Sender Name", compute="_compute_name", store=True)
    sender_id= fields.Char(string="Sender ID", )
    sender_type = fields.Selection(
        string="Sender type",
        selection=[
            ("staff", "Internal staff"),
            ("wechat", "Wechat user"),
            ("wecom", "Wecom user"),
        ],
        compute="_compute_sender_type",
    )
    partner_id = fields.Many2one("res.partner", string="Contacts",domain="[ ('is_company', '!=', 'company')]")
    employee_id = fields.Many2one("hr.employee", string="Employee")
    
    # @api.onchange("sender_id")
    # def _onchange_sender_id(self):
    #     for record in self:
    #         if record.sender_id:
    #             record.sender_type = "wecom"
    #         else:
    #             record.sender_type = "staff"

    @api.depends('partner_id', 'employee_id','sender_id',)
    def _compute_name(self):
        for record in self:
            if record.partner_id:
                record.name = record.partner_id.name
            elif record.employee_id:
                record.name = record.employee_id.name
            else:
                if "wo-" in record.sender_id or "wm-" in record.sender_id:
                    record.name = record.sender_id[-6:] #截取倒数第6位到结尾 
                else:
                    record.name = record.sender_id

    @api.depends('sender_id',)
    def _compute_sender_type(self):
        """
        计算发送者类型
        """
        for record in self:
            if "wo-" in record.sender_id or "wm-" in record.sender_id:
                type = record.sender_id.split("-")[0]   #取出第一个字符  
                if type=="wo":
                    record.sender_type="wecom"
                elif type=="wm":
                    record.sender_type="wechat"
            else:
                record.sender_type="staff"
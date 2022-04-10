# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class WecomModifyExternalSenderName(models.TransientModel):
    _name = "wecom.modify.external_sender_name"
    _table = "wecom_modify_external_sender_name"
    _description = "Wecom modify external sender name"

    chatdata_id = fields.Many2one(
        "wecom.chat.data", string="Related Chat Data", required=True, readonly=True
    )
    sender = fields.Many2one(string="Related Sender",related="chatdata_id.sender", readonly=True,required=True)

    sender_partner_id = fields.Many2one(string="Contacts",related="sender.partner_id", readonly=False)

    sender_employee_id = fields.Many2one(string="Employee",related="sender.employee_id", readonly=False)

    sender_name = fields.Char(string="Sender name",related="sender.name", readonly=False,required=True,compute="_compute_name")
    sender_type = fields.Selection(string="Sender type",related="sender.sender_type", readonly=True)


    @api.onchange("sender_employee_id")
    def _onchange_sender_employee_id(self):
        self.sender_name = self.sender_employee_id.name
        # if self.sender_partner_id:
        #     raise ValidationError(_("You have selected a contact, you can't select another employee."))

    @api.onchange("sender_partner_id")
    def _onchange_sender_partner_id(self):
        self.sender_name = self.sender_partner_id.name
        # if self.sender_employee_id:
        #     raise ValidationError(_("You have selected an employee, you can't select a contact."))

    @api.depends('sender', 'sender_partner_id','sender_employee_id',)
    def _compute_name(self):
        for record in self:
            if record.sender_partner_id:
                record.name = record.sender_partner_id.name
            elif record.sender_employee_id:
                record.name = record.sender_employee_id.name
            else:
                record.name = record.sender.name

            

    def save(self):
        """
        保存修改后的发送者名称
        """
        if self.sender_partner_id:
            self.sender.sudo().write({
                "partner_id":self.sender_partner_id.id,
                "name":self.sender_partner_id.name,
            })
            self.chatdata_id.sudo().write({
                "partner_id_of_sender":self.sender_partner_id.id,
            })  
        elif self.sender_employee_id:
            self.sender.sudo().write({
                "employee_id":self.sender_employee_id.id,
                "name":self.sender_employee_id.name,
            })
            self.chatdata_id.sudo().write({
                "employee_id_of_sender":self.sender_employee_id.id,
            })
        else:
            self.sender.sudo().write({
                "name":self.sender_name,
            })
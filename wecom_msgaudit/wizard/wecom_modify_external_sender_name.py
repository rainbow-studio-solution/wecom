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

    sender_partner_id = fields.Many2one(string="Contacts,Priority",related="sender.partner_id", readonly=False)

    sender_employee_id = fields.Many2one(string="Employee",related="sender.employee_id", readonly=False)

    sender_name = fields.Char(string="Sender name",related="sender.name", readonly=False,required=True)


    # @api.onchange("sender_employee_id")
    # def _onchange_sender_employee_id(self):
    #     if self.sender_partner_id:
    #         raise ValidationError(_("You have selected a contact, you can't select another employee."))

    # @api.onchange("sender_partner_id")
    # def _onchange_sender_partner_id(self):
    #     if self.sender_employee_id:
    #         raise ValidationError(_("You have selected an employee, you can't select a contact."))

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
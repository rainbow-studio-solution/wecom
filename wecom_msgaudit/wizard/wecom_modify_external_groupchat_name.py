# -*- coding: utf-8 -*-

from numpy import require
from odoo import api, fields, models

class WecomModifyExternalGroupchatName(models.TransientModel):
    _name = "wecom.modify.external_groupchat_name"
    _table = "wecom_modify_external_groupchat_name"
    _description = "Wecom modify external groupcha name"

    chatdata_id = fields.Many2one(
        "wecom.chat.data", string="Related Chat Data", required=True, readonly=True
    )

    room = fields.Many2one(string="Related Group chat",related="chatdata_id.room", readonly=True,required=True)
    room_name = fields.Char(string="Group chat name",related="room.room_name", readonly=False,required=True)

    def save(self):
        """
        保存修改后的外部群名称
        """
        print(self.chatdata_id.room)
        self.room.sudo().write({
            # "name":self.room_name,
            "room_name":self.room_name
        })

# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    def hide_hr_menu(self):
        """
        一键隐藏HR菜单
        :return:
        """
        domain = ['&','&','&',('parent_id','=',False),('web_icon', 'ilike', 'hr'),('name', 'not like', 'HRM'),'|',('active','=',True),('active','=',False)]

        self.env["ir.ui.menu"].search(domain).sudo().write({"active": False})
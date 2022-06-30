# -*- coding: utf-8 -*-


from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # 应用菜单
    menu_app_id = fields.Many2one(related="company_id.menu_app_id", readonly=False)
    menu_agentid = fields.Integer(related="menu_app_id.agentid", readonly=False)
    menu_secret = fields.Char(related="menu_app_id.secret", readonly=False)
    menu_body = fields.Text(related="menu_app_id.menu_body", readonly=False)

    def get_menu_app_info(self):
        """
        获取应用信息
        :return:
        """
        for record in self:
            if record.menu_agentid == 0 or record.menu_secret == "":
                raise UserError(_("Portal application ID and secret cannot be empty!"))
            else:
                record.menu_app_id.get_app_info()

    def get_wecom_app_menu(self):
        """
        获取企微应用菜单
        """
        result = self.menu_app_id.get_wecom_app_menu()
        if result["state"]:
            self.menu_body = result["body"]
            result["msg"].update(
                {"next": {"type": "ir.actions.act_window_close"},}
            )
            return self.env["wecomapi.tools.action"].WecomSuccessNotification(
                result["msg"]
            )
        else:
            return self.env["wecomapi.tools.action"].ApiExceptionDialog(
                result["msg"], raise_exception=True
            )

    def delete_wecom_app_menu(self):
        """
        删除企微应用菜单
        """
        result = self.menu_app_id.delete_wecom_app_menu()
        if result["state"]:
            self.menu_body = "{}"
            result["msg"].update(
                {"next": {"type": "ir.actions.act_window_close"},}
            )
            return self.env["wecomapi.tools.action"].WecomSuccessNotification(
                result["msg"]
            )
        else:
            return self.env["wecomapi.tools.action"].ApiExceptionDialog(
                result["msg"], raise_exception=True
            )

    def init_wecom_app_menu(self):
        """
        初始化企微应用菜单
        """
        result = self.menu_app_id.set_wecom_app_menu()
        if result["state"]:
            self.menu_body = result["body"]
            result["msg"].update(
                {"next": {"type": "ir.actions.act_window_close"},}
            )
            return self.env["wecomapi.tools.action"].WecomSuccessNotification(
                result["msg"]
            )
        else:
            return self.env["wecomapi.tools.action"].ApiExceptionDialog(
                result["msg"], raise_exception=True
            )

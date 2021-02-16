# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID, _


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    contacts_secret = fields.Char(
        "Contact Secret", config_parameter="wxwork.contacts_secret"
    )
    contacts_access_token = fields.Char(
        string="Contact token",
        readonly=True,
        config_parameter="wxwork.contacts_access_token",
    )
    contacts_auto_sync_hr_enabled = fields.Boolean(
        "Allow Enterprise WeChat Contacts are automatically updated to HR",
        default=True,
    )
    # contacts_sync_img_enabled = fields.Boolean(
    #     '允许同步Enterprise WeChat图片', config_parameter='wxwork.contacts_sync_img_enabled', )
    contacts_img_path = fields.Char(
        "Enterprise WeChat Picture storage path",
        config_parameter="wxwork.contacts_img_path",
    )
    contacts_sync_hr_department_id = fields.Integer(
        "Enterprise WeChat department ID to be synchronized",
        config_parameter="wxwork.contacts_sync_hr_department_id",
        default=1,
    )
    contacts_edit_enabled = fields.Boolean(
        "Allow API to edit Enterprise WeChat contacts",
        default=False,
        # readonly=True,
    )
    contacts_sync_user_enabled = fields.Boolean(
        "Allow Enterprise WeChat contacts to automatically update system accounts",
        default=False,
    )
    contacts_always_update_avatar_enabled = fields.Boolean(
        "Always update avatar", default=False,
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ir_config = self.env["ir.config_parameter"].sudo()

        contacts_auto_sync_hr_enabled = (
            True
            if ir_config.get_param("wxwork.contacts_auto_sync_hr_enabled") == "True"
            else False
        )
        contacts_edit_enabled = (
            True
            if ir_config.get_param("wxwork.contacts_edit_enabled") == "True"
            else False
        )
        contacts_sync_user_enabled = (
            True
            if ir_config.get_param("wxwork.contacts_sync_user_enabled") == "True"
            else False
        )
        contacts_always_update_avatar_enabled = (
            True
            if ir_config.get_param("wxwork.contacts_always_update_avatar_enabled")
            == "True"
            else False
        )

        res.update(
            contacts_auto_sync_hr_enabled=contacts_auto_sync_hr_enabled,
            contacts_edit_enabled=contacts_edit_enabled,
            contacts_sync_user_enabled=contacts_sync_user_enabled,
            contacts_always_update_avatar_enabled=contacts_always_update_avatar_enabled,
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ir_config = self.env["ir.config_parameter"].sudo()
        ir_config.set_param("wxwork.debug_enabled", self.debug_enabled or "False")
        ir_config.set_param(
            "wxwork.contacts_auto_sync_hr_enabled",
            self.contacts_auto_sync_hr_enabled or "False",
        )
        ir_config.set_param(
            "wxwork.contacts_edit_enabled", self.contacts_edit_enabled or "False"
        )
        ir_config.set_param(
            "wxwork.contacts_sync_user_enabled",
            self.contacts_sync_user_enabled or "False",
        )
        ir_config.set_param(
            "wxwork.contacts_always_update_avatar_enabled",
            self.contacts_always_update_avatar_enabled or "False",
        )

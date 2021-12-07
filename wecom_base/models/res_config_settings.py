# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )

    # 基础
    is_wecom_organization = fields.Boolean(
        related="company_id.is_wecom_organization", readonly=False
    )
    company_name = fields.Char(related="company_id.display_name", string="Company Name")
    abbreviated_name = fields.Char(related="company_id.abbreviated_name")
    corpid = fields.Char(string="Corp ID", related="company_id.corpid", readonly=False)

    debug_enabled = fields.Boolean("Turn on debug mode", default=True)

    resources_path = fields.Char(
        "WeCom resources storage path",
        config_parameter="wecom.resources_path",
    )

    # 通讯录
    contacts_secret = fields.Char(related="company_id.contacts_secret", readonly=False)

    contacts_access_token = fields.Char(related="company_id.contacts_access_token")

    contacts_auto_sync_hr_enabled = fields.Boolean(
        related="company_id.contacts_auto_sync_hr_enabled", readonly=False
    )

    contacts_sync_hr_department_id = fields.Integer(
        related="company_id.contacts_sync_hr_department_id", readonly=False
    )

    contacts_edit_enabled = fields.Boolean(
        related="company_id.contacts_edit_enabled", readonly=False
    )

    contacts_sync_user_enabled = fields.Boolean(
        related="company_id.contacts_sync_user_enabled", readonly=False
    )

    contacts_use_system_default_avatar = fields.Boolean(
        related="company_id.contacts_use_system_default_avatar", readonly=False
    )
    contacts_update_avatar_every_time_sync = fields.Boolean(
        related="company_id.contacts_update_avatar_every_time_sync", readonly=False
    )

    @api.onchange("contacts_use_system_default_avatar")
    def _onchange_contacts_use_system_default_avatar(self):
        if self.contacts_use_system_default_avatar:
            self.contacts_update_avatar_every_time_sync = False

    # JS API
    corp_jsapi_ticket = fields.Char(
        "Enterprise JS API Ticket",
        related="company_id.corp_jsapi_ticket",
        readonly=True,
    )

    agent_jsapi_ticket = fields.Char(
        "Application JS API Ticket",
        related="company_id.agent_jsapi_ticket",
        readonly=True,
    )

    jsapi_debug = fields.Boolean(
        "JS API Debug mode",
        config_parameter="wecom.jsapi_debug",
        default=False,
    )

    js_api_list = fields.Char(
        "JS API Inertface List",
        related="company_id.js_api_list",
        readonly=False,
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ir_config = self.env["ir.config_parameter"].sudo()

        debug_enabled = (
            True if ir_config.get_param("wecom.debug_enabled") == "True" else False
        )

        res.update(
            debug_enabled=debug_enabled,
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ir_config = self.env["ir.config_parameter"].sudo()
        ir_config.set_param("wecom.debug_enabled", self.debug_enabled or "False")

    def open_wecom_company(self):
        return {
            "type": "ir.actions.act_window",
            "name": "My Company",
            "view_mode": "form",
            "res_model": "res.company",
            "res_id": self.env.company.id,
            "target": "current",
            "context": {
                "form_view_initial_mode": "edit",
            },
        }

    @api.depends("company_id")
    def _compute_wecom_company_corpid(self):
        company_corpid = self.company_id.corpid if self.company_id.corpid else ""

        for record in self:
            record.wecom_company_corpid = company_corpid

    @api.model
    def open_wecom_settings(self):

        action = self.env["ir.actions.actions"]._for_xml_id(
            "wecom_base.res_config_settings_view_form"
        )
        action["target"] = "new"

        return action

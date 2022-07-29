# -*- coding: utf-8 -*-

from random import weibullvariate
from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # 基础
    is_wecom_organization = fields.Boolean(
        related="company_id.is_wecom_organization", readonly=False
    )
    company_name = fields.Char(
        related="company_id.name", string="Company Name", readonly=False
    )
    abbreviated_name = fields.Char(
        related="company_id.abbreviated_name", readonly=False
    )
    corpid = fields.Char(string="Corp ID", related="company_id.corpid", readonly=False)

    debug_enabled = fields.Boolean("Turn on debug mode", default=True)

    resources_path = fields.Char(
        "WeCom resources storage path", config_parameter="wecom.resources_path",
    )

    global_error_code_url = fields.Char(
        "Global error code page URL", config_parameter="wecom.global_error_code_url",
    )

    global_error_code_troubleshooting_method_node = fields.Char(
        "Global error code troubleshooting method page element node", config_parameter="wecom.global_error_code_troubleshooting_method_node",
    )

    module_wecom_web_theme = fields.Boolean("WeCom Web Theme")
    module_wecom_contacts = fields.Boolean("WeCom Contacts")


    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ir_config = self.env["ir.config_parameter"].sudo()

        debug_enabled = (
            True if ir_config.get_param("wecom.debug_enabled") == "True" else False
        )

        res.update(debug_enabled=debug_enabled,)
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
            "context": {"form_view_initial_mode": "edit",},
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

    def get_app_info(self):
        """
        获取企业应用信息
        :param agentid:
        :return:
        """

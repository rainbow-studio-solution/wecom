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
    wxwork_company_name = fields.Char(
        related="company_id.display_name", string="Current company name"
    )
    wxwork_company_corpid = fields.Char(
        string="Enterprise ID", compute="_compute_wxwork_company_corpid"
    )
    wxwork_company_count = fields.Integer(
        "Number of Companies", compute="_compute_wxwork_company_count"
    )


    debug_enabled = fields.Boolean("Turn on debug mode", default=True)

    img_path = fields.Char(
        "Enterprise WeChat Picture storage path", config_parameter="wxwork.img_path",
    )

    # module_wxwork_auth_oauth = fields.Boolean(
    #     "Use Enterprise weChat scan code to verify login (OAuth)",
    # )
    # module_wxwork_hr_syncing = fields.Boolean(
    #     "Installation Enterprise WeChat HR synchronization function",
    # )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ir_config = self.env["ir.config_parameter"].sudo()

        debug_enabled = (
            True if ir_config.get_param("wxwork.debug_enabled") == "True" else False
        )

        res.update(debug_enabled=debug_enabled,)
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ir_config = self.env["ir.config_parameter"].sudo()
        ir_config.set_param("wxwork.debug_enabled", self.debug_enabled or "False")

    @api.depends("company_id")
    def _compute_wxwork_company_count(self):
        company_count = self.env["res.company"].sudo().search_count([])
        for record in self:
            record.wxwork_company_count = company_count

    def open_wxwork_company(self):
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
    def _compute_wxwork_company_corpid(self):
        company_corpid = self.company_id.corpid if self.company_id.corpid else ""

        for record in self:
            record.wxwork_company_corpid = company_corpid

# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    del_wecom_tag = fields.Boolean("Delete wecom tag", default=False)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ir_config = self.env["ir.config_parameter"].sudo()

        del_wecom_tag = (
            True if ir_config.get_param("wecom.del_wecom_tag") == "True" else False
        )

        res.update(
            del_wecom_tag=del_wecom_tag,
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ir_config = self.env["ir.config_parameter"].sudo()
        ir_config.set_param("wecom.del_wecom_tag", self.del_wecom_tag or "False")

    def hide_hr_menu(self):
        """
        一键隐藏HR菜单
        :return:
        """
        domain = [
            "&",
            "&",
            "&",
            ("parent_id", "=", False),
            ("web_icon", "ilike", "hr"),
            ("name", "not like", "HRM"),
            "|",
            ("active", "=", True),
            ("active", "=", False),
        ]

        self.env["ir.ui.menu"].search(domain).sudo().write({"active": False})
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }

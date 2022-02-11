# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )

    # 通讯录
    material_app_id = fields.Many2one(
        related="company_id.material_app_id", readonly=False,
    )

    material_agentid = fields.Integer(related="material_app_id.agentid", readonly=False)
    material_secret = fields.Char(related="material_app_id.secret", readonly=False)
    material_access_token = fields.Char(related="material_app_id.access_token")

    def get_material_app_info(self):
        """
        获取应用信息
        :return:
        """
        for record in self:
            print(record.material_agentid,record.material_secret)
            if record.material_agentid== 0 or record.material_secret == '':
                raise UserError(_("Material application ID and secret cannot be empty!"))
            else:
                record.material_app_id.get_app_info()
 

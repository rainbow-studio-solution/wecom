# -*- coding: utf-8 -*-

import base64
import os
import io
from PIL import Image
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )

    # 消息
    message_app_id = fields.Many2one(
        related="company_id.message_app_id", readonly=False
    )
    message_agentid = fields.Integer(related="message_app_id.agentid", readonly=False)
    message_secret = fields.Char(related="message_app_id.secret", readonly=False)
    message_access_token = fields.Char(related="message_app_id.access_token")
    # wecom_message_logo = fields.Binary(
    #     related="company_id.wecom_message_logo", readonly=False
    # )
    # wecom_message_logo_web = fields.Binary(
    #     related="company_id.wecom_message_logo_web", readonly=False
    # )

    # message_agentid = fields.Char(related="company_id.message_agentid", readonly=False)

    # message_secret = fields.Char(related="company_id.message_secret", readonly=False)

    # module_gamification = fields.Boolean(readonly=False)

    # module_wecom_hr_gamification_message = fields.Boolean(
    #     related="company_id.module_wecom_hr_gamification_message", readonly=False
    # )

    # module_digest = fields.Boolean("KPI Digests")
    # module_wxowrk_digest_message = fields.Boolean(
    #     "Send KPI Digests periodically via WeCom",
    # )

    # module_stock = fields.Boolean()
    # module_wecom_stock_message = fields.Boolean(
    #     related="company_id.module_wecom_stock_message", readonly=False
    # )

    # module_purchase = fields.Boolean()
    # module_wecom_purchase_message = fields.Boolean(
    #     "Send Purchase message via WeCom",
    # )

    # @api.onchange("wecom_message_logo")
    # def _onchange_wecom_message_logo(self):
    #     if self.wecom_message_logo:
    #         image = tools.base64_to_image(self.wecom_message_logo)
    #         w, h = image.size
    #         if w == h:
    #             self.wecom_message_logo_web = tools.image_process(
    #                 self.wecom_message_logo, size=(180, 180)
    #             )
    #         else:
    #             raise UserError(_("Please upload a picture of the square!"))

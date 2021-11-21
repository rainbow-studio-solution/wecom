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

    square_logo = fields.Binary(related="company_id.square_logo", readonly=False)
    square_logo_web = fields.Binary(
        related="company_id.square_logo_web", readonly=False
    )

    message_agentid = fields.Char(related="company_id.message_agentid", readonly=False)

    message_secret = fields.Char(related="company_id.message_secret", readonly=False)

    module_gamification = fields.Boolean(
        related="company_id.module_gamification", readonly=False
    )

    module_wecom_hr_gamification_message = fields.Boolean(
        related="company_id.module_wecom_hr_gamification_message", readonly=False
    )

    # module_digest = fields.Boolean(related="company_id.module_digest", readonly=False)
    # module_wxowrk_digest_message = fields.Boolean(
    #     related="company_id.module_wxowrk_digest_message", readonly=False
    # )

    module_digest = fields.Boolean("KPI Digests")
    module_wxowrk_digest_message = fields.Boolean(
        "Send KPI Digests periodically via WeCom",
    )

    module_stock = fields.Boolean(related="company_id.module_stock", readonly=False)
    module_wecom_stock_message = fields.Boolean(
        related="company_id.module_wecom_stock_message", readonly=False
    )

    module_purchase = fields.Boolean()
    module_wecom_purchase_message = fields.Boolean(
        "Send Purchase message via WeCom",
    )

    @api.onchange("square_logo")
    def _onchange_square_logo(self):
        if self.square_logo:
            image = tools.base64_to_image(self.square_logo)
            w, h = image.size
            if w == h:
                self.square_logo_web = tools.image_process(
                    self.square_logo, size=(180, 180)
                )
            else:
                raise UserError(_("Please upload a picture of the square!"))

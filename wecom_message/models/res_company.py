# -*- coding: utf-8 -*-

import base64
import os
import io
from PIL import Image
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class Company(models.Model):
    _inherit = "res.company"

    def _get_square_logo(self):
        return base64.b64encode(
            open(
                os.path.join(
                    tools.config["root_path"],
                    "addons",
                    "wecom_message",
                    "static",
                    "img",
                    "logo.png",
                ),
                "rb",
            ).read()
        )

    message_agentid = fields.Char(
        "Message Agent Id",
        default="0000000",
    )

    message_secret = fields.Char(
        "Message Secret",
        default="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    )

    square_logo = fields.Binary(
        string="WeCom Square logo",
        default=_get_square_logo,
        readonly=False,
    )
    square_logo_web = fields.Binary(
        store=True,
        attachment=False,
    )  # compute="_compute_square_logo",

    module_gamification = fields.Boolean(
        "",
    )
    module_wecom_hr_gamification_message = fields.Boolean(
        "Send messages to motivate users via WeCom",
    )

    module_digest = fields.Boolean(
        "KPI Digests",
    )
    module_wxowrk_digest_message = fields.Boolean(
        "Send KPI Digests periodically via WeCom",
    )

    module_stock = fields.Boolean(
        "",
    )
    module_wecom_stock_message = fields.Boolean(
        "Send Inventory message via WeCom",
    )

    # module_purchase = fields.Boolean("",)
    # module_wecom_purchase_message = fields.Boolean(
    #     "Send Purchase message via WeCom",
    # )

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

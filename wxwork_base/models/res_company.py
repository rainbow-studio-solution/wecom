# -*- coding: utf-8 -*-

import base64
import io
import logging
import os

from odoo import api, fields, models, tools, _
from odoo.tools.translate import translate


class Company(models.Model):
    _inherit = "res.company"

    def _get_square_logo(self):
        return base64.b64encode(
            open(
                os.path.join(
                    tools.config["root_path"],
                    "addons",
                    "base",
                    "static",
                    "img",
                    "res_company_logo.png",
                ),
                "rb",
            ).read()
        )

    # abbreviated_name = fields.Char("Abbreviated Name", required=True, translate=True)
    abbreviated_name = fields.Char("Abbreviated Name", translate=True)
    square_logo = fields.Binary(
        string="Enterprise wechat Square logo",
        default=_get_square_logo,
        readonly=False,
    )
    square_logo_web = fields.Binary(
        compute="_compute_square_logo", store=True, attachment=False
    )
    is_wxwork_organization = fields.Boolean(
        "Enterprise wechat organization", default=False
    )
    corpid = fields.Char("Enterprise ID", default="xxxxxxxxxxxxxxxxxx")

    @api.depends("square_logo")
    def _compute_square_logo(self):
        for company in self:
            company.square_logo_web = tools.image_process(
                company.square_logo, size=(180, 0)
            )

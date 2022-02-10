# -*- coding: utf-8 -*-

import base64
import os
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from odoo.modules.module import get_module_resource


class Company(models.Model):
    _inherit = "res.company"

    # 消息
    message_app_id = fields.Many2one(
        "wecom.apps",
        string="Application",
        # required=True,
        # default=lambda self: self.env.company,
        domain="[('company_id', '=', current_company_id)]",
    )

    # def _get_wecom_message_logo(self):
    #     image_path = get_module_resource("wecom_message", "static/src/img", "logo.png")
    #     with tools.file_open(image_path, "rb") as f:
    #         return base64.b64encode(f.read())

    # message_agentid = fields.Char(
    #     "Message Agent Id",
    #     default="0000000",
    # )

    # message_secret = fields.Char(
    #     "Message Secret",
    #     default="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    # )

    # wecom_message_logo = fields.Binary(
    #     string="WeCom Message logo", default=_get_wecom_message_logo, readonly=False
    # )
    # wecom_message_logo_web = fields.Binary(
    #     store=True,
    #     attachment=False,
    #     compute="_onchange_wecom_message_logo",
    # )  #

    # @api.depends("wecom_message_logo")
    # def _compute_wecom_message_logo(self):
    #     for company in self:
    #         company.wecom_message_logo_web = tools.image_process(
    #             company.wecom_message_logo, size=(180, 480)
    #         )

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

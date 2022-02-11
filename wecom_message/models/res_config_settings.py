# -*- coding: utf-8 -*-

import base64
import os
import io
from PIL import Image
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError


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

    message_app_callback_service_ids = fields.One2many(
        related="message_app_id.app_callback_service_ids", readonly=False
    )

    # module_gamification = fields.Boolean(readonly=False)

    # module_wecom_hr_gamification_message = fields.Boolean(
    #     related="company_id.module_wecom_hr_gamification_message", readonly=False
    # )

    module_digest = fields.Boolean("KPI Digests")
    module_wecom_digest_message = fields.Boolean(
        "Send KPI Digests periodically via WeCom",
    )

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

    def generate_parameters(self):
        """
        生成参数
        :return:
        """
        code = self.env.context.get("code")
        if bool(code) and code == "message":
            for record in self:
                if not record.message_app_id:
                    raise ValidationError(_("Please bind message app!"))
                else:
                    record.message_app_id.with_context(code=code).generate_parameters()
        super(ResConfigSettings, self).generate_parameters()

    def generate_service(self):
        """
        生成服务
        :return:
        """
        code = self.env.context.get("code")
        if bool(code) and code == "message":
            for record in self:
                if not record.message_app_id:
                    raise ValidationError(_("Please bind message app!"))
                else:
                    record.message_app_id.with_context(code=code).generate_service()
        super(ResConfigSettings, self).generate_service()

    def get_message_app_info(self):
        """
        获取应用信息
        :return:
        """
        for record in self:
            if record.message_agentid == 0 or record.message_secret == '':
                raise UserError(_("Message application ID and secret cannot be empty!"))
            else:
                record.message_app_id.get_app_info()

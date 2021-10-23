# -*- coding: utf-8 -*-

import base64
from odoo import api, fields, models, tools, _
from odoo.modules.module import get_resource_path


class Company(models.Model):
    _inherit = "res.company"

    def _default_qrcode(self):
        image_path = get_resource_path(
            "website_china_extends", "static/src/img", "qrcode.png"
        )
        with tools.file_open(image_path, "rb") as f:
            return base64.b64encode(f.read())

    social_wechat = fields.Binary("WeChat QR code", default=_default_qrcode)
    social_wechat_kf = fields.Binary(
        "WeChat customer service QR code", compute="_compute_customer_service_qrcode",
    )
    social_wechat_kf_compute = fields.Binary(
        "WeChat customer service QR code", readonly=False,
    )
    social_qq = fields.Integer("QQ number")
    social_weibo = fields.Char("Weibo Account url")
    social_renren = fields.Char("Renren Account url")

    @api.depends("social_wechat_kf_compute")
    def _compute_customer_service_qrcode(self):
        # 判断是否存在 企业微信模块的 微信客服二维码 字段
        for record in self:
            if record._fields.get("customer_service_qrcode"):
                # print("存在")
                wechat_kf = record.customer_service_qrcode
            else:
                # print("不存在")
                wechat_kf = record.social_wechat_kf_compute
            record.social_wechat_kf = wechat_kf

    def baidu_map_img(self, zoom=15, width=298, height=298):
        partner = self.sudo().partner_id
        # return partner and partner.baidu_map_img(zoom, width, height) or None
        return (
            partner
            and partner.baidu_map_img(zoom=zoom, width=width, height=height)
            or None
        )

    def baidu_map_link(self):
        partner = self.sudo().partner_id
        return partner and partner.baidu_map_link() or None

# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
import logging
import hashlib
from Crypto.Cipher import AES
import xml.etree.cElementTree as ET
import hashlib


_logger = logging.getLogger(__name__)


class WecomApiToolsSecurity(models.AbstractModel):
    _name = "wecomapi.tools.security"
    _description = "Wecom API Tools - Security"

    def generate_jsapi_signature(self, company, nonceStr, timestamp, url):
        """
        使用sha1加密算法，生成JSAPI的签名
        ------------------------------
        company: 公司
        nonceStr: 生成签名的随机串
        timestamp: 生成签名的时间戳
        url: 当前网页的URL， 不包含#及其后面部分
        """

        # 生成签名前，刷新 ticke  .search([(("is_wecom_organization", "=", True))])
        # company.sudo().get_jsapi_ticket()

        params = self.env["ir.config_parameter"].sudo()
        base_url = params.get_param("web.base.url")

        ticket = company.corp_jsapi_ticket

        str = ("jsapi_ticket=%s&noncestr=%s&timestamp=%s&url=%s") % (
            ticket,
            nonceStr,
            timestamp,
            url,
        )
        encrypts = hashlib.sha1(str.encode("utf-8")).hexdigest()
        return encrypts


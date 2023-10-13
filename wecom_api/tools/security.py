# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
import logging
import hashlib
import random
import hashlib
from Crypto.Cipher import AES
from passlib.context import CryptContext
import xml.etree.cElementTree as ET
import hashlib


_logger = logging.getLogger(__name__)

NUMLIST = ["0","1","2","3","4","5","6","7","8","9","q","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z","A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","W","R","S","T","U","V","W","X","Y","Z",]
        

class WecomApiToolsSecurity(models.AbstractModel):
    _name = "wecomapi.tools.security"
    _description = "Wecom API Tools - Security"

    def random_str(self, num):
        """
        生成随机字符串
        :return:
        """
        rang = num
        if rang == None:
            random_str = "".join(random.choice(NUMLIST) for i in range(8))
        else:
            random_str = "".join(random.choice(NUMLIST) for i in range(int(rang)))
        return random_str

    def random_passwd(self, num):
        """
        生成随机密码
        :return:
        """        
        rang = num
        if rang == None:
            passwd = "".join(random.choice(NUMLIST) for i in range(8))
        else:
            passwd = "".join(random.choice(NUMLIST) for i in range(int(rang)))

        crypt_context = CryptContext(
            schemes=["pbkdf2_sha512", "plaintext"], deprecated=["plaintext"]
        )
        hash_password = (
            crypt_context.hash
            if hasattr(crypt_context, "hash")
            else crypt_context.encrypt
        )
        return hash_password(passwd)

    def generate_jsapi_signature(self, jsapi_ticket, nonceStr, timestamp):
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

        ICP = self.env["ir.config_parameter"].sudo()
        web_base_url = ICP.get_param("web.base.url", default="http://localhost:8069")
        if web_base_url[-1] == "/":
            web_base_url = web_base_url + "web"
        else:
            web_base_url = web_base_url + "/web"

        jsapi_ticket_str = ("jsapi_ticket=%s&noncestr=%s&timestamp=%s&url=%s") % (
            jsapi_ticket,
            nonceStr,
            timestamp,
            web_base_url,
        )
        encrypts = hashlib.sha1(jsapi_ticket_str.encode("utf-8")).hexdigest()
        return encrypts

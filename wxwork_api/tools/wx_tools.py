# -*- coding: utf-8 -*-

from PIL import Image
import os
import base64
import random
import html2text
import platform
from passlib.context import CryptContext

from odoo import api, models, tools
from datetime import datetime, timedelta


class WxTools(models.AbstractModel):
    _name = "wxwork.tools"
    _description = "Enterprise WeChat Tools"
    # def __init__(self, value):
    #     self.value = value
    #     self.result = None

    def cheeck_overdue(self, datetime_start_str, datetime_end_str, maxtime):
        """
        检查是否超期
        :return: True: 超期
                 False：未超期
        """
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        start_time = datetime.strptime(datetime_start_str, DATETIME_FORMAT)
        end_time = datetime.strptime(datetime_end_str, DATETIME_FORMAT)
        print(start_time, end_time)
        diff = end_time - start_time
        if diff < timedelta(days=maxtime):
            return True
        else:
            return False

    def path_is_exists(self, path, subpath):
        """
        检文件夹路径是否存在，不存在则创建路径
        return:返回路径
        """
        if platform.system() == "Windows":
            filepath = path.replace("\\", "/") + subpath + "/"
        else:
            filepath = path + subpath + "/"
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        return filepath

    def html2text_handle(self, body_html):
        # 转换markdown格式
        if bool(body_html):
            return html2text.html2text(body_html)
        else:
            return None

    def str2bool(self):
        """
        字符串转布尔值
        :param val: 字符串
        :return: 布尔值
        """
        # return self.value.lower() in ("yes", "true", "t", "1")

        if self.value.lower() in ["true", "t", "1"]:
            return True
        elif self.value.lower() in ["false", "f", "0"]:
            return False
        else:
            return False

    def check_dictionary_keywords(self, dictionary, key):
        """
        检查字典中是否存在key
        """
        # dictionary, key = (self.value[0], self.value[1])
        if key in dictionary.keys():
            return dictionary[key]
        else:
            return None

    def wxwork_user_enable(self):
        """
        企业微信用户是否启用
        :param value:
        :return:
        """
        if self.value == "0":
            self.result = False
        if self.value == "1":
            self.result = True
        return self.result

    def encode_image_as_base64(self):
        if not self.value:
            pass
        else:
            with open(self.value, "rb") as f:
                encoded_string = base64.b64encode(f.read())
            return encoded_string

    def gender(self, sex):
        """
        性别转换
        """
        if sex == "1":
            return "male"
        elif sex == "2":
            return "female"
        else:
            return "other"

    def is_exists(self):
        """
        判断是否存在值
        :return:
        """
        if not self.value:
            self.result = False
        else:
            self.result = True
        return self.result

    def mail_is_exists(self):
        """
        判断是否存在值
        :return:
        """
        if not self.value:
            self.result = ""
        else:
            self.result = self.value
        return self.result

    def random_passwd(self, num):
        """
        生成随机密码
        :return:
        """
        __numlist = [
            "0",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "q",
            "b",
            "c",
            "d",
            "e",
            "f",
            "g",
            "h",
            "i",
            "j",
            "k",
            "l",
            "m",
            "n",
            "o",
            "p",
            "q",
            "r",
            "s",
            "t",
            "u",
            "v",
            "w",
            "x",
            "y",
            "z",
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
            "G",
            "H",
            "I",
            "J",
            "K",
            "L",
            "M",
            "N",
            "O",
            "P",
            "W",
            "R",
            "S",
            "T",
            "U",
            "V",
            "W",
            "X",
            "Y",
            "Z",
        ]
        rang = num
        if rang == None:
            passwd = "".join(random.choice(__numlist) for i in range(8))
        else:
            passwd = "".join(random.choice(__numlist) for i in range(int(rang)))

        crypt_context = CryptContext(
            schemes=["pbkdf2_sha512", "plaintext"], deprecated=["plaintext"]
        )
        hash_password = (
            crypt_context.hash
            if hasattr(crypt_context, "hash")
            else crypt_context.encrypt
        )
        return hash_password(passwd)


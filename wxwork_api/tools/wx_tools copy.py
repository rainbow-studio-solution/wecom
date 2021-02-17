# -*- coding: utf-8 -*-

from PIL import Image
import os
import base64
import random
import html2text
import platform
from passlib.context import CryptContext
from odoo import tools

from odoo import api, models


class WxTools(object):
    def __init__(self, value):
        self.value = value
        self.result = None

    def path_is_exists(self, path=None, subpath=None):
        """
        检文件夹路径是否存在，不存在则创建路径
        return:返回路径
        """
        print(path, subpath)
        if platform.system() == "Windows":
            filepath = path.replace("\\", "/") + subpath + "/"
        else:
            filepath = path + subpath + "/"
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        return filepath

    def html2text_handle(self):
        # 转换markdown格式
        if bool(self.value):
            self.result = html2text.html2text(self.value)
        else:
            self.result = None
        return self.result

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

    def check_dictionary_keywords(self):
        """
        检查字典中是否存在key
        """
        dictionary, key = (self.value[0], self.value[1])
        if key in dictionary.keys():
            self.result = dictionary[key]
        else:
            self.result = None
        return self.result

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

    def gender(self):
        """
        性别转换
        """
        if self.value == "1":
            self.result = "male"
        elif self.value == "2":
            self.result = "female"
        else:
            self.result = "other"
        return self.result

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

    def random_passwd(self):
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
        rang = self.value
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
        self.result = hash_password(passwd)
        return self.result


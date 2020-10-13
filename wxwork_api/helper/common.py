# -*- coding: utf-8 -*-

from PIL import Image

import base64
import urllib
import os

import random
from passlib.context import CryptContext


class Common(object):
    def __init__(self, value):
        self.value = value
        self.result = None

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
        self.result = CryptContext(["pbkdf2_sha512"]).encrypt(passwd)
        return self.result


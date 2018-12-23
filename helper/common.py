# -*- coding: utf-8 -*-
import requests
import base64
from urllib.request import urlopen
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

class Common(object):
    def __init__(self, value):
        self.value = value
        self.result = None

    def str_to_bool(self):
        """
        字符串转布尔值
        :param val: 字符串
        :return: 布尔值
        """
        if self.value == 'False':
            self.result = ""
        if self.value == 'True':
            self.result = True
        return self.result

    def wxwork_user_enable(self):
        """
        企业微信用户是否启用
        :param value:
        :return:
        """
        if self.value =='0':
            self.result = False
        if self.value =='1':
            self.result = True
        return self.result

    def avatar2image(self):
        """
            头像转换
        """
        if not self.value:
            pass
        else:
            # res = requests.get(self.value)
            self.result = base64.b64encode(urlopen(self.value).read())
        return self.result

    def gender(self):
        """
            性别转换
        """
        if self.value == "1":
            self.result = 'male'
        elif self.value == "2":
            self.result = 'female'
        else:
            self.result = 'other'
        return self.result

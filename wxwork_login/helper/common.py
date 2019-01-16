# -*- coding: utf-8 -*-

import base64
import requests as req
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
from io import BytesIO
import random
from passlib.context import CryptContext

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
            response = req.get(self.value) # 将这个图片保存在内存
            self.result = base64.b64encode(BytesIO(response.content).read()) #得到这个图片的base64编码
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

    def is_exists(self):
        '''
        判断是否存在值
        :return:
        '''
        if not self.value:
            self.result = False
        else:
            self.result = True
        return self.result

    def mail_is_exists(self):
        '''
        判断是否存在值
        :return:
        '''
        if not self.value:
            self.result = ''
        else:
            self.result = self.value
        return self.result

    def random_str(self):
        '''
        生成随机字符串
        :return:
        '''
        __numlist = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'q', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
                     'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D',
                     'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'W', 'R', 'S', 'T', 'U', 'V', 'W', 'X',
                     'Y', 'Z']
        rang = self.value
        if rang == None:
            passwd = "".join(random.choice(__numlist) for i in range(8))
        else:
            passwd = "".join(random.choice(__numlist) for i in range(int(rang)))
        self.result =  passwd
        return self.result



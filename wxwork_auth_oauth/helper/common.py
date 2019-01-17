# -*- coding: utf-8 -*-

import random


class Common(object):
    def __init__(self, value):
        self.value = value
        self.result = None

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



# -*- coding: utf-8 -*-


import urllib, os, platform, cv2
import numpy as np
import time
import logging
from threading import Thread, Lock

from ...wxwork_api.CorpApi import *

_logger = logging.getLogger(__name__)


# start 以下为解决 image file is truncated (18 bytes not processed)错误
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
# end 以上为解决 image file is truncated (18 bytes not processed)错误

class SyncImage(object):
    def __init__(self, kwargs):
        self.kwargs = kwargs
        self.corpid = self.kwargs['corpid']
        self.secret = self.kwargs['secret']
        self.debug = self.kwargs['debug']
        self.department_id = self.kwargs['department_id']
        self.img_path = self.kwargs['img_path']
        self.department = self.kwargs['department']

    def run(self):
        if self.debug:
            _logger.error("开始同步企业微信通讯录-图片")
        if (platform.system() == 'Windows'):
            avatar_directory = self.img_path.replace("\\", "/") + "avatar/"
            qr_code_directory = self.img_path.replace("\\", "/") + "qr_code/"
        else:
            avatar_directory = self.img_path + "avatar/"
            qr_code_directory = self.img_path + "qr_code/"
        self.path_is_exists(avatar_directory)
        self.path_is_exists(qr_code_directory)

        user_list,avatar_urls,qr_code_urls = self.generate_image_list()
        start = time.time()
        try:
            for i in range(len(user_list)):
                remote_avatar_img = avatar_urls[i]
                local_avatar_img = avatar_directory + user_list[i] + ".jpg"

                remote_qr_code_img = qr_code_urls[i]
                local_qr_code_img = qr_code_directory + user_list[i]+ ".png"
                t1 = Thread(target=self.check_image, args=[remote_avatar_img,local_avatar_img])
                t2 = Thread(target=self.check_image, args=[remote_qr_code_img, local_qr_code_img])
                t1.start()
                t2.start()
                result = "图片同步成功"
                status ={'image_1920': True}
        except Exception as e:
            result = "图片同步失败"
            status = {'image_1920': False}
            print('同步图片错误:%s' % (repr(e)))

        end = time.time()
        times = end - start

        if self.debug:
            _logger.error("结束同步企业微信通讯录-图片，总共花费时间：%s 秒" % times)
        return times,status,result

    def generate_image_list(self):
        '''
        生成userid、avatar、qr_code的List
        :return: list
        '''

        api = CorpApi(self.corpid, self.secret)
        response = api.httpCall(
            CORP_API_TYPE['USER_LIST'],
            {
                'department_id': self.department_id,
                'fetch_child': '1',
            }
        )

        userid_list = []
        avatar_urls = []
        qr_code_urls = []
        for object in response['userlist']:
            userid_list.append(object['userid'])
            avatar_urls.append(object['avatar'])
            qr_code_urls.append(object['qr_code'])
        return userid_list,avatar_urls,qr_code_urls

    def path_is_exists(self,path):
        '''
        检文件夹路径
        :param path:
        :return:
        '''
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def check_identical_images(self,remote,local):
        '''
        比较远程图片和本地图片是否一致
        :param remote: 远程图片
        :param local: 本地图片
        :return: 布尔值
        '''
        try:
            resp = urllib.request.urlopen(remote)
            remote_img = np.asarray(bytearray(resp.read()), dtype="uint8")
            remote_img = cv2.imdecode(remote_img, cv2.IMREAD_COLOR)
            local_img = cv2.imread(local)
            difference = cv2.subtract(remote_img, local_img)
            result = not np.any(difference)
            if result is True:
                return True
            else:
                return False
        except BaseException as e:
            print(repr(e))
            return False

    def check_image(self,remote_img,local_img):
        '''
        检查是否存在本地图片，
        有：比较和更新图片
        无：下载图片
        :param remote_img: 远程图片
        :param local_img: 本地图片
        :return:
        '''
        if os.path.exists(local_img):
            # 比较本地远程和本地图片
            if not self.check_identical_images(remote_img, local_img):
                self.download_image(remote_img, local_img)
        else:
            self.download_image(remote_img, local_img)

    def download_image(self,remote_img,local_img):
        '''
        下载图片
        :param remote_img: 远程图片
        :param local_img: 本地图片
        :return:
            Ture：下载成功
            False: 下载失败
        '''
        try:
            avatar_data = urllib.request.urlopen(remote_img).read()  # 打开URL
            file_avatar = open(local_img, "wb")  # 读取，写入
            file_avatar.write(avatar_data)
            file_avatar.close()
            # return True
        except BaseException as e:
            # return False
            print(repr(e))
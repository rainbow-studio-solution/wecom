# -*- coding: utf-8 -*-
from ..api.CorpApi import *
import urllib,os,platform,cv2
import numpy as np
import time
import logging
from threading import Thread, Lock

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
        self.department_id = self.kwargs['department_id']
        self.img_path = self.kwargs['img_path']
        self.department = self.kwargs['department']
        self.times = 0
        self.result = None

    def run(self):
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
        for i in range(len(user_list)):
            remote_avatar_img = avatar_urls[i]
            local_avatar_img = avatar_directory + user_list[i]+ ".jpg"

            remote_qr_code_img = qr_code_urls[i]
            local_qr_code_img = qr_code_directory + user_list[i]+ ".png"
            # self.check_image(remote_avatar_img,local_avatar_img)
            # self.check_image(remote_qr_code_img,local_qr_code_img)
            t1 = Thread(target=self.check_image, args=[remote_avatar_img,local_avatar_img])
            t2 = Thread(target=self.check_image, args=[remote_qr_code_img, local_qr_code_img])
            t1.start()
            t2.start()
        end = time.time()
        self.times = end - start
        self.result = True
        return self.times, self.result

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
        # 是否存在本地图片
        if os.path.exists(local_img):
            # 比较本地远程和本地图片
            if not self.check_identical_images(remote_img, local_img):
                self.download_image(remote_img, local_img)
        else:
            self.download_image(remote_img, local_img)

    def download_image(self,remote_img,local_img):
        try:
            avatar_data = urllib.request.urlopen(remote_img).read()  # 打开URL
            file_avatar = open(local_img, "wb")  # 读取，写入
            file_avatar.write(avatar_data)
            file_avatar.close()
        except BaseException as e:
            print(repr(e))
# -*- coding: utf-8 -*-

from PIL import ImageFile
import os
import cv2
import logging
import platform
import time
import urllib
import threading

import numpy as np

from odoo import _
from ...wxwork_api.wx_qy_api.CorpApi import *

_logger = logging.getLogger(__name__)

# start 以下为解决 image file is truncated (18 bytes not processed)错误
ImageFile.LOAD_TRUNCATED_IMAGES = True
# end 以上为解决 image file is truncated (18 bytes not processed)错误


class SyncImage(object):
    def __init__(self, kwargs):
        self.kwargs = kwargs
        self.corpid = self.kwargs["corpid"]
        self.secret = self.kwargs["secret"]
        self.debug = self.kwargs["debug"]
        self.department_id = self.kwargs["department_id"]
        self.img_path = self.kwargs["img_path"]
        self.department = self.kwargs["department"]

    def run(self):
        if self.debug:
            _logger.info(_("Start syncing Enterprise WeChat Contact - Picture"))
        if platform.system() == "Windows":
            avatar_directory = self.img_path.replace("\\", "/") + "avatar/"
            qr_code_directory = self.img_path.replace("\\", "/") + "qr_code/"
        else:
            avatar_directory = self.img_path + "avatar/"
            qr_code_directory = self.img_path + "qr_code/"
        self.path_is_exists(avatar_directory)
        self.path_is_exists(qr_code_directory)

        user_list, avatar_urls, qr_code_urls = self.generate_image_list()
        start = time.time()
        threads = []
        """
        限制线程的最大数量为系统最大PID数量的1/800,在Linux下不做限制，很容易出现 “can't start new thread” 的错误
        """
        thread_max = int(os.getpid() / 1000)
        status = {}
        result = ""

        try:
            for i in range(len(user_list)):
                remote_avatar_img = avatar_urls[i]
                local_avatar_img = avatar_directory + user_list[i] + ".jpg"

                remote_qr_code_img = qr_code_urls[i]
                local_qr_code_img = qr_code_directory + user_list[i] + ".png"

                t1 = threading.Thread(
                    target=self.image_is_exists,
                    args=[user_list[i], remote_avatar_img, local_avatar_img],
                )
                threads.append(t1)
                t2 = threading.Thread(
                    target=self.image_is_exists,
                    args=[user_list[i], remote_qr_code_img, local_qr_code_img],
                )
                threads.append(t2)

            for t in threads:
                # 如果线程达到最大值则等待前面线程跑完空出线程位置
                t.start()
                while True:
                    # 判断正在运行的线程数量,如果小于 thread_max 则退出while循环,
                    # 进入for循环启动新的进程.否则就一直在while循环进入死循环
                    if len(threading.enumerate()) < thread_max:
                        break

                result = _("Picture synced successfully")
                status = {"image_1920": True}

        except Exception as e:
            result = _("Picture sync failed")
            status = {"image_1920": False}
            if self.debug:
                print(_("Sync picture error:%s") % (repr(e)))

        end = time.time()
        times = end - start

        if self.debug:
            _logger.info(
                _(
                    "End sync Enterprise WeChat Contact - Picture, Total time spent: %s seconds"
                )
                % times
            )
        return times, status, result

    def generate_image_list(self):
        """
        生成userid、avatar、qr_code的List
        :return: list
        """

        api = CorpApi(self.corpid, self.secret)
        response = api.httpCall(
            CORP_API_TYPE["USER_LIST"],
            {
                "department_id": self.department_id,
                "fetch_child": "1",
            },
        )

        userid_list = []
        avatar_urls = []
        qr_code_urls = []
        for object in response["userlist"]:
            userid_list.append(object["userid"])
            avatar_urls.append(object["avatar"])
            qr_code_urls.append(object["qr_code"])
        return userid_list, avatar_urls, qr_code_urls

    def path_is_exists(self, path):
        """
        检文件夹路径
        :param path:
        :return:
        """
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def check_images(self, user_name, remote, local):
        """
        比较远程图片和本地图片是否一致
        :param remote: 远程图片
        :param local: 本地图片
        :return: 布尔值
        """
        # print(_("compare pictures %s") % user_name)
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
            if self.debug:
                print(
                    _("Failed to compare pictures %s,error: %s") % (user_name, repr(e))
                )
            pass

    def image_is_exists(self, user_name, remote_img, local_img):
        """
        检查是否存在本地图片，
        有：比较和更新图片
        无：下载图片
        :param remote_img: 远程图片
        :param local_img: 本地图片
        :return:
        """
        if os.path.exists(local_img):
            # 比较本地远程和本地图片
            if not self.check_images(user_name, remote_img, local_img):
                self.download_image(user_name, remote_img, local_img)
        else:
            self.download_image(user_name, remote_img, local_img)

    def download_image(self, user_name, remote_img, local_img):
        """
        下载图片
        :param remote_img: 远程图片
        :param local_img: 本地图片
        :return:
            Ture：下载成功
            False: 下载失败
        """
        try:
            avatar_data = urllib.request.urlopen(remote_img).read()  # 打开URL
            file_avatar = open(local_img, "wb")  # 读取，写入
            file_avatar.write(avatar_data)
            file_avatar.close()
            # return True
        except BaseException as e:
            if self.debug:
                print(
                    _("Failed to download image of %s error: %s") % (user_name, repr(e))
                )

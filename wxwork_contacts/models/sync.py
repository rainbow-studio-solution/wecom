# -*- coding: utf-8 -*-

from odoo import api
from ..api.CorpApi import *
from ..helper.common import *
import base64,urllib,os,platform,cv2
import numpy as np
import time
import logging
from threading import Thread, Lock
import threading
from queue import Queue
from .sync_image import SyncImage
from ..models.res_users import *

_logger = logging.getLogger(__name__)


# start 以下为解决 image file is truncated (18 bytes not processed)错误
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
# end 以上为解决 image file is truncated (18 bytes not processed)错误

class SyncTask(object):
    def __init__(self, kwargs):
        self.kwargs = kwargs
        self.users = self.kwargs['users']
    def run(self):
        _logger.error("开始同步企业微信通讯录")
        threads = []
        task_name_list = ['企业微信图片同步','企业微信用户同步']
        task_func_list = [SyncImage(self.kwargs).run,self.users.sync_user]
        times = []
        results = []
        statuses = {}
        for i in range(len(task_name_list)):
            thread_task = SyncTaskThread(task_func_list[i], task_name_list[i])
            threads.append(thread_task)
        for i in range(len(task_name_list)):
            threads[i].start()
        for i in range(len(task_name_list)):
            threads[i].join()

        for t in threads:
            if t.is_alive():
                pass
            else:
                time, status, result = t.result
                times.append(time)
                statuses.update(status)
                results.append(result)
        results = '\n'.join(results)
        return sum(times),statuses,results

class SyncTaskThread(Thread):
    def __init__(self, func, name=''):
        Thread.__init__(self)
        self.name = name
        self.func = func
        self.result = self.func()

    def get_result(self):
        try:
            return self.result
        except Exception:
            return None

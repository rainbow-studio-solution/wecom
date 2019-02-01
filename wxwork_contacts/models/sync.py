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

_logger = logging.getLogger(__name__)


# start 以下为解决 image file is truncated (18 bytes not processed)错误
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
# end 以上为解决 image file is truncated (18 bytes not processed)错误


class SyncTask(object):
    def __init__(self, kwargs):
        self.kwargs = kwargs
        self.corpid = self.kwargs['corpid']
        self.secret = self.kwargs['secret']
        self.department_id = self.kwargs['department_id']
        self.img_path = self.kwargs['img_path']
        self.department = self.kwargs['department']
        self.lock = Lock()

    def run(self):

        print(self.kwargs)
        thread_sync_image = threading.Thread(target=SyncImage.run, args=[self.kwargs])

        thread_sync_image.start()

        thread_sync_image.join()





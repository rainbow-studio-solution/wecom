# -*- coding: utf-8 -*-

import time
from odoo import api, models, tools, _
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class WecomApiToolsDatetime(models.AbstractModel):
    _name = "wecomapi.tools.datetime"
    _description = "Wecom API Tools - Datetime"

    def timestamp2datetime(self, time_stamp):
        """
        时间戳转日期时间
        """
        if len(str(time_stamp)) > 10:
            # 一般爬取下来的时间戳长度都是13位的数字，而time.localtime的参数要的长度是10位，所以我们需要将其/1000并取整即可
            time_stamp = int(time_stamp / 1000)
        loc_time = time.localtime(time_stamp)
        return time.strftime("%Y-%m-%d %H:%M:%S", loc_time)

    def cheeck_days_overdue(self, datetime_start, maxday):
        """[summary]
        检查天数是否超期
        Args:
            datetime_start_str ([type]): [description]
            datetime_end_str ([type]): [description]
            maxday ([type]): [description] 天数

        Returns:
            True: 超期
            False：未超期
        """

        now = datetime.now()
        # print(now - datetime_start)
        if datetime_start > (now - timedelta(days=maxday)):
            return False
        else:
            return True

    def cheeck_hours_overdue(self, datetime_start, maxhour):
        """[summary]
        检查小时是否超期
        Args:
            datetime_start_str ([type]): [description]
            datetime_end_str ([type]): [description]
            maxhour ([type]): [description] 小时

        Returns:
            True: 超期
            False：未超期
        """

        now = datetime.now()
        if datetime_start > (now - timedelta(hours=maxhour)):
            return False
        else:
            return True

    def cheeck_minutes_overdue(self, datetime_start, maxminute):
        """[summary]
        检查分钟是否超期
        Args:
            datetime_start_str ([type]): [description]
            datetime_end_str ([type]): [description]
            maxminute ([type]): [description] 分钟

        Returns:
            True: 超期
            False：未超期
        """

        now = datetime.now()

        if datetime_start > (now - timedelta(minutes=maxminute)):
            return False
        else:
            return True

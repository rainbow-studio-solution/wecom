# -*- coding: utf-8 -*-

import logging
from threading import Thread
from .sync_image import SyncImage

_logger = logging.getLogger(__name__)

class SyncTask(object):
    def __init__(self, kwargs):
        self.kwargs = kwargs
        self.sync_hr = self.kwargs['sync_hr']
        # self.sync_user = self.kwargs['sync_user']
        # self.users = self.kwargs['users']
        self.department = self.kwargs['department']
        self.employee = self.kwargs['employee']

    def run(self):
        _logger.error("开始同步企业微信通讯录")
        if self.sync_hr:
            threads = []
            # if self.sync_user:
            #     task_name_list = ['企业微信图片同步','企业微信部门同步','企业微信员工同步','企业微信用户绑定']
            #     task_func_list = [
            #         SyncImage(self.kwargs).run,
            #         self.department.sync_department,
            #         self.employee.sync_employee,
            #         # self.employee.binding,
            #     ]
            # else:
            # _logger.error("当前设置不允许从企业微信同步到User")
            task_name_list = ['企业微信图片同步', '企业微信部门同步', '企业微信员工同步']
            task_func_list = [
                SyncImage(self.kwargs).run,
                self.department.sync_department,
                self.employee.sync_employee,
            ]
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
                    statuses.update(status)
                    times.append(time)
                    results.append("%s，花费时间：%s 秒" % (result,round(time,3)))
            results = '\n'.join(results)
            _logger.error("结束同步企业微信通讯录，总共花费时间：%s 秒" % sum(times))
            return sum(times),statuses,results
        else:
            _logger.error("同步终止，当前设置不允许从企业微信同步到odoo")

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

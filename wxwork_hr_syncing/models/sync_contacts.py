# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, _
from threading import Thread
from .sync_image import SyncImage
from .sync_department import SyncDepartment
from .sync_department_category import SyncDepartmentCategory

_logger = logging.getLogger(__name__)


class SyncTask(object):
    """
    同步HR任务
    """

    def __init__(self, kwargs):
        self.kwargs = kwargs
        self.debug = self.kwargs["debug"]
        self.img_path = self.kwargs["img_path"]
        self.sync_hr = self.kwargs["sync_hr"]
        self.sync_avatar = self.kwargs["sync_avatar"]
        self.always_sync_avatar = self.kwargs["always_sync_avatar"]
        self.company = self.kwargs["company"]
        self.department = self.kwargs["department"]
        self.department_category = self.kwargs["department_category"]
        self.employee = self.kwargs["employee"]
        self.employee_category = self.kwargs["employee_category"]

    def run(self):
        if self.debug:
            _logger.info(
                _("Start to synchronize the enterprise wechat contact of %s."),
                self.company.name,
            )

        times = []
        results = []

        if self.sync_hr:
            threads = []

            # 任务名称列表
            task_name_list = [
                _("Enterprise WeChat department synchronization"),
                _("Enterprise WeChat department tag synchronization"),
                # _("Enterprise WeChat employee synchronization"),
                # _("Enterprise WeChat employee tag synchronization"),
            ]

            # 任务方法列表
            task_func_list = [
                SyncDepartment(self.kwargs).run,
                SyncDepartmentCategory(self.kwargs).run,
                # self.employee.sync_employee,
                # self.employee_category.sync_employee_tags,
            ]

            if self.sync_avatar:
                # 如果允许同步头像
                task_name_list.insert(0, _("Enterprise WeChat picture synchronization"))
                task_func_list.insert(0, SyncImage(self.kwargs).run)

            # statuses = {}
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
                    # time, status, result = t.result
                    time, result = t.result

                    # statuses.update(status)
                    times.append(time)
                    results.append(
                        _("%s, time spent: " "%s seconds") % (result, round(time, 3))
                    )

            results = "\n".join(results)
            if self.debug:
                _logger.info(
                    _(
                        "End sync Enterprise WeChat Contact, total time spent: %s seconds"
                    )
                    % sum(times)
                )

            # return sum(times), statuses, results

        else:
            if self.debug:
                _logger.warning(
                    "The synchronization is terminated, the current setting does not allow synchronization from enterprise WeChat to odoo"
                )

        return sum(times), results


class SyncTaskThread(Thread):
    def __init__(self, func, name=""):
        Thread.__init__(self)
        self.name = name
        self.func = func
        self.result = self.func()

    def get_result(self):
        try:
            return self.result
        except Exception:
            return None

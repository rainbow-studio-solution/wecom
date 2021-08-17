# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, _
from threading import Thread

# from .sync_image import SyncImage
from .sync_department import SyncDepartment
from .sync_employee import SyncEmployee
from .sync_tag import SyncTag

_logger = logging.getLogger(__name__)


class SyncTask(object):
    def __init__(self, kwargs):
        self.kwargs = kwargs
        self.debug = self.kwargs["debug"]

    def run(self):
        if self.debug:
            _logger.info(
                _("Start to synchronize the enterprise wechat contact of %s."),
                self.kwargs["company"].name,
            )

        times = []
        results = []

        if self.kwargs["company"].contacts_auto_sync_hr_enabled:
            threads = []

            # 任务名称列表
            task_name_list = [
                _("Enterprise WeChat department synchronization"),
                _("Enterprise WeChat employee synchronization"),
                _("Enterprise WeChat tag synchronization"),
            ]

            # 任务方法列表
            task_func_list = [
                SyncDepartment(self.kwargs).run,
                SyncEmployee(self.kwargs).run,
                SyncTag(self.kwargs).run,
            ]

            # if self.kwargs["company"].contacts_download_avatar_enabled:
            #     # 如果允许下载头像
            #     task_name_list.insert(0, _("Enterprise WeChat picture synchronization"))
            #     task_func_list.insert(0, SyncImage(self.kwargs).run)

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

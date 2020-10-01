# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, _
from threading import Thread
from .sync_image import SyncImage

_logger = logging.getLogger(__name__)


class SyncTask(object):
    def __init__(self, kwargs):
        self.kwargs = kwargs
        self.debug = self.kwargs["debug"]
        self.sync_hr = self.kwargs["sync_hr"]
        # self.sync_user = self.kwargs['sync_user']
        # self.users = self.kwargs['users']
        self.department = self.kwargs["department"]
        self.employee = self.kwargs["employee"]

    def run(self):
        if self.debug:
            _logger.info(_("Start syncing Enterprise WeChat Contact"))
        if self.sync_hr:
            threads = []

            task_name_list = [
                _("Enterprise WeChat picture synchronization"),
                _("Enterprise WeChat department synchronization"),
                _("Enterprise WeChat employee synchronization"),
            ]
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
                    results.append(
                        _("%s, time spent: %s seconds") % (result, round(time, 3))
                    )
            results = "\n".join(results)
            if self.debug:
                _logger.info(
                    _(
                        "End sync Enterprise WeChat Contact, total time spent: %s seconds"
                    )
                    % sum(times)
                )
            return sum(times), statuses, results
        else:
            if self.debug:
                _logger.warning(
                    _(
                        "The synchronization is terminated, the current setting does not allow synchronization from enterprise WeChat to odoo"
                    )
                )


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

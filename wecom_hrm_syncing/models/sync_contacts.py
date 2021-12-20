# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, _
from threading import Thread

# from .sync_image import SyncImage
# from .sync_department import SyncDepartment
# from .sync_employee import SyncEmployee
# from .sync_tag import SyncTag

_logger = logging.getLogger(__name__)


class SyncTask(models.AbstractModel):
    _name = "wecom.sync_task"
    _description = "Wecom Synchronization task"

    def run(self, company):

        params = self.env["ir.config_parameter"].sudo()
        debug = params.get_param("wecom.debug_enabled")
        if debug:
            _logger.info(
                _("Start to synchronize the WeCom contact of %s."), company.name,
            )

        times = []
        results = []

        # 部门同步
        times1, result1 = self.env["wecom.sync_task_department"].run(company)
        # results = "\n".join(result1)
        results.append(result1)
        times.append(times1)

        # 人员同步
        times2, result2 = self.env["wecom.sync_task_employee"].run(company)
        # results = "\n".join(result2)
        results.append(result2)
        times.append(times2)

        # 标签同步
        times3, result3 = self.env["wecom.sync_task_tag"].run(company)
        # results = "\n".join(result3)
        results.append(result3)
        times.append(times3)

        # else:
        #     if debug:
        #         _logger.warning(
        #             _(
        #                 "The synchronization is terminated, the current setting does not allow synchronization from WeCom to odoo"
        #             )
        #         )

        return sum(times), results

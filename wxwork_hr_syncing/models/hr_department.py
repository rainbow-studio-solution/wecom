# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import Warning
import time
import logging
import json
from ...wxwork_api.wx_qy_api.CorpApi import *


_logger = logging.getLogger(__name__)


class SyncDepartment(models.Model):

    _inherit = "hr.department"

    def sync_department(self):
        params = self.env["ir.config_parameter"].sudo()
        corpid = params.get_param("wxwork.corpid")
        secret = params.get_param("wxwork.contacts_secret")
        debug = params.get_param("wxwork.debug_enabled")

        sync_department_id = params.get_param("wxwork.contacts_sync_hr_department_id")

        if debug:
            _logger.info(
                _(
                    "Start to synchronize Enterprise WeChat Contact - Department Synchronization"
                )
            )
        wxapi = CorpApi(corpid, secret)

        # 获取企业微信部门LIST
        try:
            response = wxapi.httpCall(
                CORP_API_TYPE["DEPARTMENT_LIST"], {"id": sync_department_id,},
            )
            start1 = time.time()
            for obj in response["department"]:
                self.run_sync(obj, debug)
            end1 = time.time()
            times1 = end1 - start1

            start2 = time.time()
            self.run_set(debug)

            end2 = time.time()
            times2 = end2 - start2

            times = times1 + times2
            result = _("Department synchronization successful")
            status = {"department": True}
        except Exception as e:
            times = time.time()
            result = _("Department synchronization failed")
            status = {"department": False}
            if debug:
                print(_("Department synchronization failed, error: %s", e))

        times = times
        if debug:
            _logger.info(
                _(
                    "End sync Enterprise WeChat Contact - Department Synchronization,Total time spent: %s seconds"
                )
                % times
            )
        return times, status, result

    def run_sync(self, wxwork_department, debug):
        """
        执行同步部门
        """

        # 查询数据库是否存在相同的企业微信部门ID，有则更新，无则新建

        department = self.sudo().search(
            [
                ("wxwork_department_id", "=", wxwork_department["id"]),
                ("is_wxwork_department", "=", True),
                "|",
                ("active", "=", True),
                ("active", "=", False),
            ],
            limit=1,
        )

        if not department:
            self.create_department(department, wxwork_department, debug)
        else:
            self.update_department(department, wxwork_department, debug)

    def create_department(self, records, obj, debug):
        try:
            records.create(
                {
                    "name": obj["name"],
                    "wxwork_department_id": obj["id"],
                    "wxwork_department_parent_id": obj["parentid"],
                    "wxwork_department_order": obj["order"],
                    "is_wxwork_department": True,
                }
            )
            result = True
        except Exception as e:
            if debug:
                print(_("department: %s - %s") % (obj["name"], repr(e)))
            result = False
        return result

    def update_department(self, records, obj, debug):
        try:
            records.write(
                {
                    "name": obj["name"],
                    "wxwork_department_parent_id": obj["parentid"],
                    "wxwork_department_order": obj["order"],
                    "is_wxwork_department": True,
                }
            )
            result = True
        except Exception as e:
            if debug:
                print(_("department:%s - %s") % (obj["name"], repr(e)))
            result = False
        return result

    def run_set(self, debug):
        """由于json数据是无序的，故在同步到本地数据库后，需要设置新增企业微信部门的上级部门"""
        result = True
        departments = self.search([("is_wxwork_department", "=", True),])
        try:
            for department in departments:
                if not department.wxwork_department_id:
                    pass
                else:
                    department.write(
                        {
                            "parent_id": self.get_parent_department(
                                department, departments
                            ).id,
                        }
                    )
            result = True
        except Exception as e:
            if debug:
                print(
                    _("Department: The parent department setting of %s failed")
                    % repr(e)
                )
            result = False
        return result

    def get_parent_department(self, department, departments):
        """
        获取上级部门
        """
        parent_department = departments.search(
            [
                ("wxwork_department_id", "=", department.wxwork_department_parent_id),
                ("is_wxwork_department", "=", True),
            ]
        )
        return parent_department

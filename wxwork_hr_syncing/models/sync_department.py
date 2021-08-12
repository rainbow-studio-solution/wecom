# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import Warning
import time
import logging
import json

from odoo.addons.wxwork_api.api.corp_api import CorpApi, CORP_API_TYPE

_logger = logging.getLogger(__name__)


class SyncDepartment(object):
    def __init__(self, kwargs):
        self.kwargs = kwargs
        self.corpid = self.kwargs["company"].corpid
        self.secret = self.kwargs["company"].contacts_secret
        self.debug = self.kwargs["debug"]
        self.company = self.kwargs["company"]
        self.department_id = self.kwargs["company"].contacts_sync_hr_department_id
        self.department = self.kwargs["department"]

    def run(self):
        """[summary]
        运行同步
        """
        if self.debug:
            _logger.info(
                _("Start synchronizing departments of %s"), self.company.name,
            )

        wxapi = CorpApi(self.corpid, self.secret)

        result = ""
        times = 0
        try:
            response = wxapi.httpCall(
                CORP_API_TYPE["DEPARTMENT_LIST"], {"id": str(self.department_id),},
            )
            # response 为 dict
            # response["department"] 为 list

            # 清洗数据
            departments = self.department_data_cleaning(response["department"])

            start1 = time.time()
            for obj in departments:
                self.run_sync_department(obj)
            end1 = time.time()
            times1 = end1 - start1

            start2 = time.time()
            self.run_set_department()
            end2 = time.time()
            times2 = end2 - start2

            times = times1 + times2
            result = _("Department synchronization successful")

            # status = {"department": True}

        except Exception as e:
            times = time.time()
            result = _("Department synchronization failed")
            # status = {"department": False}
            if self.debug:
                _logger.warning(
                    _(
                        "Department error synchronizing %s, error: %s",
                        self.company.name,
                        e,
                    )
                )
        times = times
        if self.debug:
            _logger.info(
                _("End sync %s Department,Total time spent: %s seconds")
                % (self.company.name, times)
            )

        # return times, status, result
        return times, result

    def department_data_cleaning(self, departments):
        """[summary]
        部门数据清洗
        Args:
            json ([type]): [description]index
        """

        for department in departments:
            if department.get("parentid") == 1:
                department["parentid"] = 0

        for index, department in enumerate(departments):
            if department.get("id") == 1:
                del departments[index]

        return departments

    def run_sync_department(self, wxwork_department):
        """[summary]
        执行同步部门
        Args:
            wxwork_department ([type]): [description]
        """

        # 查询数据库是否存在相同的企业微信部门ID，有则更新，无则新建

        department = self.department.sudo().search(
            [
                ("wxwork_department_id", "=", wxwork_department["id"]),
                ("is_wxwork_department", "=", True),
                ("company_id", "=", self.company.id),
                "|",
                ("active", "=", True),
                ("active", "=", False),
            ],
            limit=1,
        )

        if not department:
            self.create_department(department, wxwork_department)
        else:
            self.update_department(department, wxwork_department)

    def create_department(self, records, obj):
        """[summary]
        创建部门
        Args:
            records ([type]): [description]
            obj ([type]): [description]
        """

        records.create(
            {
                "name": obj["name"],
                "wxwork_department_id": obj["id"],
                "wxwork_department_parent_id": obj["parentid"],
                "wxwork_department_order": obj["order"],
                "is_wxwork_department": True,
                "company_id": self.company.id,
            }
        )

    def update_department(self, records, obj):
        """[summary]
        更新部门
        Args:
            records ([type]): [description]
            obj ([type]): [description]
        """
        records.write(
            {
                "name": obj["name"],
                "wxwork_department_parent_id": obj["parentid"],
                "wxwork_department_order": obj["order"],
                "is_wxwork_department": True,
                "company_id": self.company.id,
            }
        )

    def run_set_department(self):
        """[summary]
        由于json数据是无序的，故在同步到本地数据库后，需要设置新增企业微信部门的上级部门
        """

        departments = self.department.sudo().search(
            [("is_wxwork_department", "=", True),]
        )

        for department in departments:
            if not department.wxwork_department_id:
                pass
            else:
                try:
                    department.write(
                        {
                            "parent_id": self.get_parent_department(
                                department, departments
                            ).id,
                        }
                    )
                except Exception as e:
                    if self.debug:
                        print(
                            _(
                                "Error setting parent department for company %s, Error details:%s"
                            )
                            % (self.company.name, repr(e))
                        )

    def get_parent_department(self, department, departments):
        """[summary]
        获取上级部门
        Args:
            department ([type]): [description]
            departments ([type]): [description]
        """
        parent_department = departments.search(
            [
                ("wxwork_department_id", "=", department.wxwork_department_parent_id),
                ("is_wxwork_department", "=", True),
            ]
        )
        return parent_department

# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import Warning
import time
import logging
import json

from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException

_logger = logging.getLogger(__name__)


class SyncDepartment(models.AbstractModel):
    _name = "wecom.sync_task_department"
    _description = "Wecom Synchronize department tasks"

    def run(self, company):
        """[summary]
        运行同步
        """
        params = self.env["ir.config_parameter"].sudo()
        debug = params.get_param("wecom.debug_enabled")
        if debug:
            _logger.info(
                _("Start synchronizing departments of %s"),
                company.name,
            )

        result = ""
        times = 0
        try:
            wxapi = self.env["wecom.service_api"].init_api(
                company, "contacts_secret", "contacts"
            )
            response = wxapi.httpCall(
                self.env["wecom.service_api_list"].get_server_api_call(
                    "DEPARTMENT_LIST"
                ),
                {
                    "id": str(company.contacts_sync_hr_department_id),
                },
            )
            # response 为 dict
            # response["department"] 为 list

            # 清洗数据
            departments = self.department_data_cleaning(response["department"])

            start1 = time.time()
            for obj in departments:
                self.run_sync_department(company, obj)
            end1 = time.time()
            times1 = end1 - start1

            start2 = time.time()
            self.run_set_department(company)
            end2 = time.time()
            times2 = end2 - start2

            times = times1 + times2
            result = (
                _("Successfully synchronized '%s''s WeCom Department") % company.name
            )
        except ApiException as e:
            times = time.time()
            result = (
                _("Failed to synchronized '%s''s WeCom Department") % company.name
            ) % (
                company.name,
                e.errMsg,
            )
            if debug:
                _logger.warning(
                    _(
                        "Department error synchronizing %s, error: %s",
                        company.name,
                        e.errMsg,
                    )
                )
        times = times
        if debug:
            _logger.info(
                _("End sync %s Department,Total time spent: %s seconds")
                % (company.name, times)
            )

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

    def run_sync_department(self, company, wecom_department):
        """[summary]
        执行同步部门
        Args:
            wecom_department ([type]): [description]
        """

        # 查询数据库是否存在相同的企业微信部门ID，有则更新，无则新建

        department = (
            self.env["hr.department"]
            .sudo()
            .search(
                [
                    ("wecom_department_id", "=", wecom_department["id"]),
                    ("is_wecom_department", "=", True),
                    ("company_id", "=", company.id),
                    "|",
                    ("active", "=", True),
                    ("active", "=", False),
                ],
                limit=1,
            )
        )

        if not department:
            self.create_department(company, department, wecom_department)
        else:
            self.update_department(company, department, wecom_department)

    def create_department(self, company, records, obj):
        """[summary]
        创建部门
        Args:
            records ([type]): [description]
            obj ([type]): [description]
        """
        try:
            records.create(
                {
                    "name": obj["name"],
                    "wecom_department_id": obj["id"],
                    "wecom_department_parent_id": obj["parentid"],
                    "wecom_department_order": obj["order"],
                    "is_wecom_department": True,
                    "company_id": company.id,
                }
            )
        except Exception as e:
            _logger.warning(
                "Error creating Department [%s], error details:%s"
                % (obj["name"], str(e))
            )

    def update_department(self, company, records, obj):
        """[summary]
        更新部门
        Args:
            records ([type]): [description]
            obj ([type]): [description]
        """
        try:
            records.write(
                {
                    "name": obj["name"],
                    "wecom_department_parent_id": obj["parentid"],
                    "wecom_department_order": obj["order"],
                    "is_wecom_department": True,
                    "company_id": company.id,
                }
            )
        except Exception as e:
            _logger.warning(
                "Error updating Department [%s], error details:%s"
                % (obj["name"], str(e))
            )

    def run_set_department(self, company):
        """[summary]
        由于json数据是无序的，故在同步到本地数据库后，需要设置新增企业微信部门的上级部门
        """
        params = self.env["ir.config_parameter"].sudo()
        debug = params.get_param("wecom.debug_enabled")

        departments = (
            self.env["hr.department"]
            .sudo()
            .search(
                [
                    ("is_wecom_department", "=", True),
                ]
            )
        )

        for department in departments:
            if not department.wecom_department_id:
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
                    if debug:
                        _logger.warning(
                            _(
                                "Error setting parent department for company %s, Error details:%s"
                            )
                            % (company.name, repr(e))
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
                ("wecom_department_id", "=", department.wecom_department_parent_id),
                ("is_wecom_department", "=", True),
            ]
        )
        return parent_department

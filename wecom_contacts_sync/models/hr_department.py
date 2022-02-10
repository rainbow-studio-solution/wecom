# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import Warning
import time
import logging
import json
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException

_logger = logging.getLogger(__name__)

class Department(models.Model):
    _inherit = "hr.department"

    # -------------------------------------------------------
    # 同步部门
    # -------------------------------------------------------
    def sync_department(self, company):
        """
        同步部门
        """
        res = {}
        start_time = time.time()
        state = None
        # 获取所有的企业微信部门
        departments = (
            self.env["hr.department"]
            .sudo()
            .search(
                [
                    ("is_wecom_department", "=", True),
                    ("company_id", "=", company.id),
                    "|",
                    ("active", "=", True),
                    ("active", "=", False),
                ],
            )
        )

        params = self.env["ir.config_parameter"].sudo()
        debug = params.get_param("wecom.debug_enabled")
        if debug:
            _logger.info(
                _("Start synchronizing departments of %s"), company.name,
            )
 
  

        try:
            app_config = self.env["wecom.app_config"].sudo()
            contacts_sync_hr_department_id = app_config.get_param(
                company.contacts_app_id.id, "contacts_sync_hr_department_id"
            )  # 需要同步的企业微信部门ID

            wxapi = self.env["wecom.service_api"].InitServiceApi(
                company.corpid, company.contacts_app_id.secret
            )
            response = wxapi.httpCall(
                self.env["wecom.service_api_list"].get_server_api_call(
                    "DEPARTMENT_LIST"
                ),
                {"id": contacts_sync_hr_department_id,},
            )
            
        except ApiException as e:
            state = "fail"

            result = _("Department error synchronizing %s, error: %s",company.name,e.errMsg)
            
            if debug:
                _logger.warning( result)
        else:
            # response 为 dict,response["department"] 为 list
            # 清洗数据
            departments = self.department_data_cleaning(response["department"])

            for obj in departments:
                self.run_sync_department(company, obj)

            self.run_set_department(company)
            state = "completed"
            result = (
                _("Successfully synchronized [%s]'s Department") % company.name
            )
        finally:
            end_time = time.time()
            if debug:
                _logger.info(
                    _("End sync %s Department,Total time spent: %s seconds")
                    % (company.name, end_time-start_time)
                )
            res.update({
                "department_sync_times":end_time-start_time,
                "department_sync_state":state,
                "department_sync_result":result,
                })
            return res
    
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
                [("is_wecom_department", "=", True), ("company_id", "=", company.id)]
            )
        )

        for department in departments:
            if not department.wecom_department_id:
                pass
            else:
                parent_department = self.get_parent_department(department, departments)
                if not parent_department:
                    pass
                else:
                    try:
                        department.write(
                            {"parent_id": parent_department.id,}
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
            departments ([type]): [descriptions]
        """
        parent_department = departments.search(
            [
                ("wecom_department_id", "=", department.wecom_department_parent_id),
                ("is_wecom_department", "=", True),
            ]
        )
        return parent_department
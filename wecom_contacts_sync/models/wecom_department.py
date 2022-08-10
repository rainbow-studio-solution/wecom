# -*- coding: utf-8 -*-

import logging
import time
from odoo import fields, models, api, Command, tools, _
from odoo.exceptions import UserError
from lxml import etree
from lxml_to_dict import lxml_to_dict
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException
from odoo.addons.base.models.ir_mail_server import MailDeliveryException

_logger = logging.getLogger(__name__)


class WecomDepartment(models.Model):
    _name = "wecom.department"
    _description = "Wecom department"
    _order = "order"

    # 企微字段
    department_id = fields.Integer(
        string="Department ID", readonly=True, default="0"
    )  # 部门id
    name = fields.Char(string="Name", readonly=True, default="")  # 部门名称
    name_en = fields.Char(string="English name", readonly=True, default="")  # 英部门文名称
    department_leader = fields.Char(
        string="Department Leader", readonly=True, default=""
    )  # 部门负责人的UserID；第三方仅通讯录应用可获取
    parentid = fields.Integer(
        string="Superior department", readonly=True, default="0",
    )  # 父部门id。根部门为1
    order = fields.Integer(
        string="Sequence", readonly=True, default="0",
    )  # 在父部门中的次序值。order值大的排序靠前。值范围是[0, 2^32)

    # odoo字段
    company_id = fields.Many2one(
        "res.company",
        required=True,
        domain="[('is_wecom_organization', '=', True)]",
        copy=False,
        store=True,
    )
    parent_id = fields.Many2one(
        "wecom.department",
        string="Parent Department",
        index=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    )
    child_ids = fields.One2many(
        "wecom.department", "parent_id", string="Child Departments"
    )
    member_ids = fields.One2many(
        "wecom.user", "department_id", string="Members", readonly=True
    )

    # ------------------------------------------------------------
    # 企微部门下载
    # ------------------------------------------------------------
    @api.model
    def download_wecom_deps(self):
        """
        下载部门列表
        """
        start_time = time.time()
        company = self.env.context.get("company_id")

        tasks = []

        try:
            wxapi = self.env["wecom.service_api"].InitServiceApi(
                company.corpid, company.contacts_app_id.secret
            )

            # 2022-08-10 按官方建议进行重构
            # 官方建议换用 获取子部门ID列表 与 获取单个部门详情 组合的方式获取部门
            response = wxapi.httpCall(
                self.env["wecom.service_api_list"].get_server_api_call(
                    "DEPARTMENT_SIMPLELIST"
                ),
            )
        except ApiException as ex:
            end_time = time.time()
            self.env["wecomapi.tools.action"].ApiExceptionDialog(
                ex, raise_exception=False
            )
            tasks = [
                {
                    "name": "download_department_data",
                    "state": False,
                    "time": end_time - start_time,
                    "msg": str(ex),
                }
            ]
        except Exception as e:
            end_time = time.time()
            tasks = [
                {
                    "name": "download_department_data",
                    "state": False,
                    "time": end_time - start_time,
                    "msg": str(e),
                }
            ]
        else:
            # 获取只有 'id' , 'parentid' , 'order' 字段的列表
            wecom_departments = response["department_id"]

            # 1.下载部门
            for wecom_department in wecom_departments:
                download_department_result = self.download_department(
                    company, wecom_department
                )
                if download_department_result:
                    for r in download_department_result:
                        tasks.append(r)

            # 2.完成下载
            end_time = time.time()
            task = {
                "name": "download_department_data",
                "state": True,
                "time": end_time - start_time,
                "msg": _("Department list downloaded successfully."),
            }
            tasks.append(task)
        finally:
            return tasks  # 返回结果

    def download_department(self, company, wecom_department):
        """
        下载部门
        """
        # 查询数据库是否存在相同的企业微信部门ID，有则更新，无则新建
        department = self.sudo().search(
            [
                ("department_id", "=", wecom_department["id"]),
                ("company_id", "=", company.id),
            ],
            limit=1,
        )
        result = {}
        try:
            wxapi = self.env["wecom.service_api"].InitServiceApi(
                company.corpid, company.contacts_app_id.secret
            )

            response = wxapi.httpCall(
                self.env["wecom.service_api_list"].get_server_api_call(
                    "DEPARTMENT_DETAILS"
                ),
                {"id": str(wecom_department["id"])},
            )
        except ApiException as ex:
            result = _(
                "Wecom API acquisition company[%s]'s department [id:%s] details failed, error details: %s"
            ) % (company.name, wecom_department["id"], str(ex))
            _logger.warning(result)
        except Exception as e:
            result = _(
                "Wecom API acquisition company[%s]'s department [id:%s] details failed, error details: %s"
            ) % (company.name, wecom_department["id"], str(e))
            _logger.warning(result)
        else:
            if not department:
                result = self.create_department(company, department, response)
            else:
                result = self.update_department(company, department, response)
        finally:
            return result

    def create_department(self, company, department, response):
        """
        创建部门
        """
        try:
            department.create(
                {
                    "name": response["name"],
                    "name_en": response["name_en"],
                    "department_leader": response["department_leader"],
                    "department_id": response["id"],
                    "parentid": response["parentid"],
                    "order": response["order"],
                    "company_id": company.id,
                }
            )
        except Exception as e:
            result = _("Error creating Department [%s], error details:%s") % (
                response["name"],
                str(e),
            )
            _logger.warning(result)
            return {
                "name": "add_department",
                "state": False,
                "time": 0,
                "msg": result,
            }

    def update_department(self, company, department, response):
        """
        更新部门
        """
        try:
            department.write(
                {
                    "name": response["name"],
                    "name_en": response["name_en"],
                    "department_leader": response["department_leader"],
                    "department_id": response["id"],
                    "parentid": response["parentid"],
                    "order": response["order"],
                }
            )
        except Exception as e:
            result = _("Error updating Department [%s], error details:%s") % (
                response["name"],
                str(e),
            )
            _logger.warning(result)
            return {
                "name": "update_department",
                "state": False,
                "time": 0,
                "msg": result,
            }

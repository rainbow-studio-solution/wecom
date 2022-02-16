# -*- coding: utf-8 -*-

import logging
import base64
import time
from lxml import etree
from odoo import api, fields, models, _
from lxml_to_dict import lxml_to_dict
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException

_logger = logging.getLogger(__name__)

WECOM_DEPARTMENT_MAPPING_ODOO_DEPARTMENT = {
    "Id": "wecom_department_id",  # 部门Id
    "Name": "name",  # 部门名称
    "ParentId": "wecom_department_parent_id",  # 父部门id
    "Order": "wecom_department_order",  # 主部门
}


class Department(models.Model):
    _inherit = "hr.department"

    category_ids = fields.Many2many(
        "hr.employee.category",
        "department_category_rel",
        "dmp_id",
        "category_id",
        groups="hr.group_hr_manager",
        string="Tags",
    )

    wecom_department_id = fields.Integer(
        string="WeCom department ID", readonly=True, default="0",
    )

    wecom_department_parent_id = fields.Integer(
        "WeCom parent department ID",
        help="Parent department ID,32-bit integer.Root department is 1",
        readonly=True,
    )
    wecom_department_order = fields.Char(
        "WeCom department sort",
        default="1",
        help="Order value in parent department. The higher order value is sorted first. The value range is[0, 2^32]",
        readonly=True,
    )
    is_wecom_department = fields.Boolean(
        string="WeCom Department", readonly=True, default=False,
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
        if not company:
            company = self.env.company
        if company.is_wecom_organization:
            try:
                wxapi = self.env["wecom.service_api"].InitServiceApi(
                    company.corpid, company.contacts_app_id.secret
                )
                app_config = self.env["wecom.app_config"].sudo()
                contacts_sync_hr_department_id = app_config.get_param(
                    company.contacts_app_id.id, "contacts_sync_hr_department_id"
                )  # 需要同步的企业微信部门ID
                response = wxapi.httpCall(
                    self.env["wecom.service_api_list"].get_server_api_call(
                        "DEPARTMENT_LIST"
                    ),
                    {"id": contacts_sync_hr_department_id,},
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
                # response 为 dict，response["department"] 为 list
                # 清洗数据
                wecom_departments = self.department_data_cleaning(
                    response["department"]
                )

                # 1.下载部门
                for wecom_department in wecom_departments:
                    download_department_result = self.download_department(
                        company, wecom_department
                    )
                    if download_department_result:
                        tasks.append(download_department_result)

                # 2.设置上级部门
                set_parent_department_result = self.set_parent_department(company)
                if set_parent_department_result:
                    tasks.append(set_parent_department_result)

                # 3.完成下载
                end_time = time.time()
                task = {
                    "name": "download_department_data",
                    "state": True,
                    "time": end_time - start_time,
                    "msg": _("Department list downloaded successfully."),
                }
                tasks.append(task)
            # finally:
            #     return tasks  # 返回失败结果
        else:
            end_time = time.time()
            tasks = [
                {
                    "name": "download_department_data",
                    "state": False,
                    "time": end_time - start_time,
                    "msg": _(
                        "The current company does not identify the enterprise wechat organization. Please configure or switch the company."
                    ),
                }
            ]  # 返回失败结果

        
        return tasks

    def department_data_cleaning(self, departments):
        """[summary]
        部门数据清洗
        删除 id 为 1 的部门
        将部门的 parentid=1 改为 parentid=0
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

    def download_department(self, company, wecom_department):
        """
        下载部门
        """
        # 查询数据库是否存在相同的企业微信部门ID，有则更新，无则新建
        department = self.sudo().search(
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
        result = {}
        if not department:
            result = self.create_department(company, department, wecom_department)
        else:
            result = self.update_department(company, department, wecom_department)
        return result

    def create_department(self, company, department, wecom_department):
        """
        创建部门
        """
        try:
            department.create(
                {
                    "name": wecom_department["name"],
                    "wecom_department_id": wecom_department["id"],
                    "wecom_department_parent_id": wecom_department["parentid"],
                    "wecom_department_order": wecom_department["order"],
                    "is_wecom_department": True,
                    "company_id": company.id,
                }
            )
        except Exception as e:
            result = _("Error creating Department [%s], error details:%s") % (
                wecom_department["name"],
                str(e),
            )
            _logger.warning(result)
            return {
                "name": "add_department",
                "state": False,
                "time":0,
                "msg": result,
            }

    def update_department(self, company, department, wecom_department):
        """
        更新部门
        """
        try:
            department.write(
                {
                    "name": wecom_department["name"],
                    "wecom_department_parent_id": wecom_department["parentid"],
                    "wecom_department_order": wecom_department["order"],
                    "is_wecom_department": True,
                    "company_id": company.id,
                }
            )
        except Exception as e:
            result = _("Error updating Department [%s], error details:%s") % (
                wecom_department["name"],
                str(e),
            )
            _logger.warning(result)
            return {
                "name": "update_department",
                "state": False,
                "time":0,
                "msg": result,
            }

    def set_parent_department(self, company):
        """[summary]
        由于json数据是无序的，故在同步到本地数据库后，需要设置新增企业微信部门的上级部门
        """
        params = self.env["ir.config_parameter"].sudo()
        debug = params.get_param("wecom.debug_enabled")

        departments = self.search(
            [("is_wecom_department", "=", True), ("company_id", "=", company.id)]
        )
        results = []
        for department in departments:
            if not department.wecom_department_id:
                pass
            else:
                parent_department = self.get_parent_department_by_wecom_department_id(
                    department, departments
                )
                if not parent_department:
                    pass
                else:
                    try:
                        department.write(
                            {"parent_id": parent_department.id,}
                        )
                    except Exception as e:
                        result = _(
                            "Error setting parent department for company %s, Error details:%s"
                        ) % (company.name, repr(e))
                        if debug:
                            _logger.warning(result)
                        results.append(
                            {
                                "name": "set_parent_department",
                                "state": False,
                                "time":0,
                                "msg": result,
                            }
                        )
        return results  # 返回失败的结果

    def get_parent_department_by_wecom_department_id(self, department, departments):
        """[summary]
        通过企微部门id 获取上级部门
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

    # ------------------------------------------------------------
    # 企微通讯录事件
    # ------------------------------------------------------------
    def wecom_event_change_contact_party(self, cmd):
        xml_tree = self.env.context.get("xml_tree")
        company_id = self.env.context.get("company_id")
        xml_tree_str = etree.fromstring(bytes.decode(xml_tree))
        dic = lxml_to_dict(xml_tree_str)["xml"]
        # print("department dic", dic)

        domain = [
            "|",
            ("active", "=", True),
            ("active", "=", False),
        ]
        department = (
            self.env["hr.department"]
            .sudo()
            .search([("company_id", "=", company_id.id)] + domain)
        )
        callback_department = department.search(
            [("wecom_department_id", "=", dic["Id"])] + domain, limit=1,
        )
        update_dict = {}
        parent_department = False
        if "ParentId" in dic:
            if dic["ParentId"] == "1":
                pass
            else:
                parent_department = department.search(
                    [("wecom_department_id", "=", int(dic["ParentId"]))], limit=1,
                )
        for key, value in dic.items():
            if (
                key == "ToUserName"
                or key == "FromUserName"
                or key == "CreateTime"
                or key == "Event"
                or key == "MsgType"
                or key == "ChangeType"
            ):
                # 忽略掉 不需要的key
                pass
            else:
                if key in WECOM_DEPARTMENT_MAPPING_ODOO_DEPARTMENT.keys():
                    if WECOM_DEPARTMENT_MAPPING_ODOO_DEPARTMENT[key] != "":
                        update_dict[
                            WECOM_DEPARTMENT_MAPPING_ODOO_DEPARTMENT[key]
                        ] = value
                else:
                    _logger.info(
                        _(
                            "There is no mapping for field [%s], please contact the developer."
                        )
                        % key
                    )
        # print("上级部门", parent_department)
        if parent_department:
            update_dict.update({"parent_id": parent_department.id})
        else:
            update_dict.update({"parent_id": False})

        update_dict.update({"company_id": company_id.id, "is_wecom_department": True})

        # print("update_dict", callback_department, update_dict)

        if cmd == "create":
            callback_department.create(update_dict)
        elif cmd == "update":
            if "wecom_department_id" in update_dict:
                del update_dict["wecom_department_id"]
            if "wecom_department_parent_id" in update_dict:
                del update_dict["wecom_department_parent_id"]
            # print("执行更新部门", update_dict)
            callback_department.write(update_dict)
        elif cmd == "delete":
            callback_department.unlink()

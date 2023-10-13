# -*- coding: utf-8 -*-

import logging
import base64
from pdb import _rstr
import time
from lxml import etree
from odoo import api, fields, models, _

import xmltodict
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException    # type: ignore

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
        string="WeCom department ID",
        readonly=True,
        default="0",
    )

    wecom_department_parent_id = fields.Integer(
        "WeCom parent department ID",
        readonly=True,
    )
    wecom_department_order = fields.Char(
        "WeCom department sort",
        default="1",
        readonly=True,
    )
    is_wecom_department = fields.Boolean(
        string="WeCom Department",
        readonly=True,
        default=False,
    )

    # ------------------------------------------------------------
    # 同步企微部门
    # ------------------------------------------------------------
    @api.model
    def sync_wecom_deps(self):
        """
        下载部门列表
        """
        start_time = time.time()
        company = self.env.context.get("company_id")
        if type(company) == int:
            company = self.env["res.company"].browse(company)

        tasks = []

        app_config = self.env["wecom.app_config"].sudo()
        contacts_sync_hr_department_id = int(
            app_config.get_param(
                company.contacts_app_id.id, "contacts_sync_hr_department_id"
            )
        )  # 需要同步的企业微信部门ID
        print(contacts_sync_hr_department_id, type(contacts_sync_hr_department_id))
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
                "time": 0,
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
                "time": 0,
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
        for department in departments:   # type: ignore
            if department.wecom_department_parent_id:
                parent_department = self.get_parent_department_by_wecom_department_id(
                    department, company
                )
                if not parent_department:
                    pass
                else:
                    try:
                        department.write(
                            {
                                "parent_id": parent_department.id,   # type: ignore
                            }
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
                                "time": 0,
                                "msg": result,
                            }
                        )
        return results  # 返回失败的结果

    def get_parent_department_by_wecom_department_id(self, department, company):
        """[summary]
        通过企微部门id 获取上级部门
        Args:
            department ([type]): [description]
            departments ([type]): [descriptions]
        """
        parent_department = self.search(
            [
                ("wecom_department_id", "=", department.wecom_department_parent_id),
                ("company_id", "=", company.id),
            ]
        )
        return parent_department

    # ------------------------------------------------------------
    # 企微通讯录事件
    # ------------------------------------------------------------
    def wecom_event_change_contact_party(self, cmd):
        xml_tree = self.env.context.get("xml_tree")
        company_id = self.env.context.get("company_id")
        xml_tree_str = etree.fromstring(bytes.decode(xml_tree))  # type: ignore
        dic = lxml_to_dict(xml_tree_str)["xml"]  # type: ignore
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
            [("wecom_department_id", "=", dic["Id"])] + domain,
            limit=1,
        )

        update_dict = {}
        parent_department = False
        if "ParentId" in dic:
            if dic["ParentId"] == "1":
                pass
            else:
                parent_department = department.search(
                    [("wecom_department_id", "=", int(dic["ParentId"]))],
                    limit=1,
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

        if parent_department:
            update_dict.update({"parent_id": parent_department.id})
        else:
            update_dict.update({"parent_id": False})

        update_dict.update({"company_id": company_id.id, "is_wecom_department": True})

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

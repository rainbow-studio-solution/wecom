# -*- coding: utf-8 -*-

import logging
import base64
from lxml import etree
from odoo import api, fields, models, _
from lxml_to_dict import lxml_to_dict

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

    def remove_obj_from_tag(self):
        """
        从标签中移除部门
        """


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

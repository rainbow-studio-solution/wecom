# -*- coding: utf-8 -*-

import logging
import base64
from lxml import etree
from odoo import api, fields, models, _
from lxml_to_dict import lxml_to_dict

_logger = logging.getLogger(__name__)

WECOM_USER_MAPPING_ODOO_EMPLOYEE_CATEGORY = {
    "TagId": "tagid",  # 标签Id
    "AddUserItems": "add_employee_ids",  # 标签中新增的成员userid列表，用逗号分隔
    "DelUserItems": "del_employee_ids",  # 标签中删除的成员userid列表，用逗号分隔
    "AddPartyItems": "add_department_ids",  # 标签中新增的部门id列表，用逗号分隔
    "DelPartyItems": "del_department_ids",  # 标签中删除的部门id列表，用逗号分隔
}


class EmployeeCategory(models.Model):

    _inherit = "hr.employee.category"

    def wecom_event_change_contact_tag(self, cmd):
        xml_tree = self.env.context.get("xml_tree")
        company_id = self.env.context.get("company_id")
        xml_tree_str = etree.fromstring(bytes.decode(xml_tree))
        dic = lxml_to_dict(xml_tree_str)["xml"]
        # print("tag dic", dic)

        callback_tag = (
            self.env["hr.employee.category"]
            .sudo()
            .search(
                [("company_id", "=", company_id.id), ("tagid", "=", dic["TagId"])],
                limit=1,
            )
        )
        domain = [
            "|",
            ("active", "=", True),
            ("active", "=", False),
        ]
        employee = (
            self.env["hr.employee"]
            .sudo()
            .search([("company_id", "=", company_id.id)] + domain)
        )
        department = (
            self.env["hr.department"]
            .sudo()
            .search([("company_id", "=", company_id.id)] + domain)
        )

        update_dict = {}

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
                if key in WECOM_USER_MAPPING_ODOO_EMPLOYEE_CATEGORY.keys():
                    if WECOM_USER_MAPPING_ODOO_EMPLOYEE_CATEGORY[key] != "":
                        update_dict[
                            WECOM_USER_MAPPING_ODOO_EMPLOYEE_CATEGORY[key]
                        ] = value
                    else:
                        _logger.info(
                            _(
                                "There is no mapping for field [%s], please contact the developer."
                            )
                            % key
                        )
        # print("update_dict", update_dict)
        add_employee_list = []
        del_employee_list = []
        add_department_list = []
        del_department_list = []

        if "add_employee_ids" in update_dict.keys():
            for wecom_userid in update_dict["add_employee_ids"].split(","):
                add_employee_list.append(
                    employee.search([("wecom_userid", "=", wecom_userid)], limit=1).id
                )
        elif "del_employee_ids" in update_dict.keys():
            for wecom_userid in update_dict["del_employee_ids"].split(","):
                del_employee_list.append(
                    employee.search([("wecom_userid", "=", wecom_userid)], limit=1).id
                )
        elif "add_department_ids" in update_dict.keys():
            for wecom_department_id in update_dict["add_department_ids"].split(","):
                add_department_list.append(
                    department.search(
                        [("wecom_department_id", "=", wecom_department_id)], limit=1,
                    ).id
                )
        elif "del_department_ids" in update_dict.keys():
            for wecom_department_id in update_dict["del_department_ids"].split(","):
                del_department_list.append(
                    department.search(
                        [("wecom_department_id", "=", wecom_department_id)], limit=1,
                    ).id
                )

        # print(
        #     add_employee_list,
        #     del_employee_list,
        #     add_department_list,
        #     del_department_list,
        # )
        if len(add_employee_list) > 0:
            callback_tag.write(
                {"employee_ids": [(4, res, False) for res in add_employee_list]}
            )
        if len(del_employee_list) > 0:
            callback_tag.write(
                {"employee_ids": [(3, res, False) for res in del_employee_list]}
            )
        if len(add_department_list) > 0:
            callback_tag.write(
                {"department_ids": [(4, res, False) for res in add_department_list]}
            )
        if len(del_department_list) > 0:
            callback_tag.write(
                {"department_ids": [(3, res, False) for res in del_department_list]}
            )

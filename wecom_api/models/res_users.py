# -*- coding: utf-8 -*-

import logging
import base64
from lxml import etree
from odoo import api, fields, models, _
from lxml_to_dict import lxml_to_dict
from odoo.exceptions import AccessError

WECOM_USER_MAPPING_ODOO_USER = {
    "UserID": "wecom_userid",  # 成员UserID
    "Name": "name",  # 成员名称
    "Mobile": "mobile",  # 手机号码
    "Email": "email",  # 邮箱
    "Status": "active",  # 激活状态：1=已激活 2=已禁用 4=未激活 已激活代表已激活企业微信或已关注微工作台（原企业号）5=成员退出
    "Telephone": "phone",
}


class User(models.Model):
    _inherit = ["res.users"]

    def wecom_event_change_contact_user(self, cmd):
        """ """
        xml_tree = self.env.context.get("xml_tree")
        company_id = self.env.context.get("company_id")
        xml_tree_str = etree.fromstring(bytes.decode(xml_tree))
        dic = lxml_to_dict(xml_tree_str)["xml"]
        # print("user dic", dic)

        domain = [
            "|",
            ("active", "=", True),
            ("active", "=", False),
        ]
        users = (
            self.env["res.users"]
            .sudo()
            .search([("company_id", "=", company_id.id)] + domain)
        )
        callback_user = users.search(
            [("wecom_userid", "=", dic["UserID"])] + domain, limit=1,
        )
        update_dict = {}
        employee = False
        # print(callback_user)
        if callback_user:
            # 如果存在，则更新
            # 用于退出企业微信又重新加入企业微信的员工
            pass
        else:
            # 如果不存在，则从 employee 进行复制属性
            cmd = "create"
            employee = (
                self.env["hr.employee"]
                .sudo()
                .search(
                    [
                        ("company_id", "=", company_id.id),
                        ("wecom_userid", "=", dic["UserID"]),
                    ]
                    + domain
                )
            )
            update_dict.update(
                {"qr_code": employee.qr_code,}
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
                if key in WECOM_USER_MAPPING_ODOO_USER.keys():
                    if WECOM_USER_MAPPING_ODOO_USER[key] != "":
                        if WECOM_USER_MAPPING_ODOO_USER[key] == "active":
                            # 状态
                            # 激活状态: 1=已激活，2=已禁用，4=未激活，5=退出企业。
                            # 已激活代表已激活企业微信或已关注微工作台（原企业号）。未激活代表既未激活企业微信又未关注微工作台（原企业号）。
                            if value == "1":
                                update_dict.update({"active": True})
                            else:
                                update_dict.update({"active": False})
                        else:
                            update_dict[WECOM_USER_MAPPING_ODOO_USER[key]] = value

        # print("update_dict", callback_user, update_dict)
        if cmd == "create":
            groups_id = (
                self.sudo().env["res.groups"].search([("id", "=", 9),], limit=1,).id
            )  # id=1是内部用户, id=9是门户用户
            update_dict.update(
                {
                    "company_ids": [(6, 0, [company_id.id])],
                    "company_id": company_id.id,
                    "notification_type": "inbox",
                    "login": update_dict["wecom_userid"].lower(),
                    "password": self.env["wecom.tools"].random_passwd(8),
                    "company_id": company_id.id,
                    "is_wecom_user": True,
                    "groups_id": [(6, 0, [groups_id])],  # 设置用户为门户用户
                }
            )
            user_id = callback_user.create(update_dict)
            # print(user_id, employee)
            if employee:
                employee.write({"user_id": user_id.id})
                employee.sudo()._sync_user(user_id, bool(employee.image_1920))
        elif cmd == "update":
            callback_user.write(update_dict)
        elif cmd == "delete":
            # 将用户归档
            callback_user.write(
                {"active": False,}
            )

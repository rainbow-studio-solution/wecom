# -*- coding: utf-8 -*-

import logging
import base64
from lxml import etree
from odoo import api, fields, models, _
from lxml_to_dict import lxml_to_dict

_logger = logging.getLogger(__name__)

WECOM_USER_MAPPING_ODOO_EMPLOYEE = {
    "UserID": "wecom_userid",  # 成员UserID
    "Name": "name",  # 成员名称;
    "Department": "department_ids",  # 成员部门列表，仅返回该应用有查看权限的部门id
    "MainDepartment": "department_id",  # 主部门
    "IsLeaderInDept": "",  # 表示所在部门是否为上级，0-否，1-是，顺序与Department字段的部门逐一对应
    "DirectLeader": "",  # 直属上级
    "Mobile": "mobile_phone",  # 手机号码
    "Position": "job_title",  # 职位信息
    "Gender": "",  # 性别，1表示男性，2表示女性
    "Email": "work_email",  # 邮箱;
    "Status": "active",  # 激活状态：1=已激活 2=已禁用 4=未激活 已激活代表已激活企业微信或已关注微工作台（原企业号）5=成员退出
    "Avatar": "avatar",  # 头像url。注：如果要获取小图将url最后的”/0”改成”/100”即可。
    "Alias": "alias",  # 成员别名
    "Telephone": "work_phone",  # 座机;
    "Address": "work_location",  # 地址;
    "ExtAttr": {
        "Type": "",  # 扩展属性类型: 0-本文 1-网页
        "Text": "",  # 文本属性类型，扩展属性类型为0时填写
        "Value": "",  # 文本属性内容
        "Web": "",  # 网页类型属性，扩展属性类型为1时填写
        "Title": "",  # 网页的展示标题
        "Url": "",  # 网页的url
    },  # 扩展属性;
}


class HrEmployeePrivate(models.Model):
    _inherit = "hr.employee"
    _order = "wecom_user_order"

    wecom_userid = fields.Char(string="WeCom user Id", readonly=True,)
    wecom_open_userid = fields.Char(string="WeCom open user Id", readonly=True,)
    alias = fields.Char(string="Alias", readonly=True,)
    english_name = fields.Char(string="English Name", readonly=True,)

    department_ids = fields.Many2many(
        "hr.department", string="Multiple departments", readonly=True,
    )
    use_system_avatar = fields.Boolean(readonly=True, default=True)
    avatar = fields.Char(string="Avatar")

    qr_code = fields.Char(
        string="Personal QR code",
        help="Personal QR code, Scan can be added as external contact",
        readonly=True,
    )
    wecom_user_order = fields.Char(
        "WeCom user sort",
        default="0",
        help="The sort value within the department, the default is 0. The quantity must be the same as the department, The greater the value the more sort front.The value range is [0, 2^32)",
        readonly=True,
    )
    is_wecom_user = fields.Boolean(
        string="WeCom employees", readonly=True, default=False,
    )

    def remove_obj_from_tag(self):
        """
        从标签中移除员工
        """

    def unbind_wecom_member(self):
        """
        解除绑定企业微信成员
        """
        self.write(
            {"is_wecom_user": False, "wecom_userid": None, "qr_code": None,}
        )
        if self.user_id:
            # 关联了User
            self.user_id.write(
                {"is_wecom_user": False, "wecom_userid": None, "qr_code": None,}
            )


    def wecom_event_change_contact_user(self, cmd):
        """
        通讯录事件变更员工
        """
        xml_tree = self.env.context.get("xml_tree")
        company_id = self.env.context.get("company_id")
        xml_tree_str = etree.fromstring(bytes.decode(xml_tree))
        dic = lxml_to_dict(xml_tree_str)["xml"]
        # print("hr dic", dic)
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

        callback_employee = employee.search(
            [("wecom_userid", "=", dic["UserID"])] + domain, limit=1,
        )
        if callback_employee:
            # 如果存在，则更新
            # 用于退出企业微信又重新加入企业微信的员工
            cmd = "update"
        update_dict = {}
        department_ids = []  # 多部门
        new_parent_employee = False
        for key, value in dic.items():
            if key == "DirectLeader":
                parent_employee_wecom_id = value
                if parent_employee_wecom_id is None:
                    # 直属上级为空
                    new_parent_employee = False
                else:
                    # 处理直属上级
                    if "," in value:
                        parent_employee_wecom_id = value.split(",")[0]

                    new_parent_employee = employee.search(
                        [("wecom_userid", "=", parent_employee_wecom_id)], limit=1
                    )
            elif (
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
                if key in WECOM_USER_MAPPING_ODOO_EMPLOYEE.keys():
                    if WECOM_USER_MAPPING_ODOO_EMPLOYEE[key] != "":
                        if WECOM_USER_MAPPING_ODOO_EMPLOYEE[key] == "department_ids":
                            # 部门列表
                            departments = value.split(",")
                            for department in departments:
                                if department == 1:
                                    pass
                                else:
                                    odoo_department = (
                                        self.env["hr.department"]
                                        .sudo()
                                        .search(
                                            [
                                                (
                                                    "wecom_department_id",
                                                    "=",
                                                    department,
                                                ),
                                                ("company_id", "=", company_id.id),
                                                ("is_wecom_department", "=", True),
                                            ],
                                            limit=1,
                                        )
                                    )
                                    if len(odoo_department) > 0:
                                        department_ids.append(odoo_department.id)
                        elif WECOM_USER_MAPPING_ODOO_EMPLOYEE[key] == "department_id":
                            # 主部门
                            department_id = self.env["hr.department"].search(
                                [("wecom_department_id", "=", value)], limit=1
                            )
                            update_dict.update({"department_id": department_id.id})
                        elif WECOM_USER_MAPPING_ODOO_EMPLOYEE[key] == "active":
                            # 状态
                            # 激活状态: 1=已激活，2=已禁用，4=未激活，5=退出企业。
                            # 已激活代表已激活企业微信或已关注微工作台（原企业号）。未激活代表既未激活企业微信又未关注微工作台（原企业号）。
                            if value == "1":
                                update_dict.update({"active": True})
                            else:
                                update_dict.update({"active": False})
                        else:
                            update_dict[WECOM_USER_MAPPING_ODOO_EMPLOYEE[key]] = value
                else:
                    _logger.info(
                        _(
                            "There is no mapping for field [%s], please contact the developer."
                        )
                        % key
                    )
        
        # 更新直属上级字典
        if new_parent_employee:
            update_dict.update({"parent_id": new_parent_employee.id})
        else:
            update_dict.update({"parent_id": False,"coach_id": False})

        if len(department_ids) > 0:
            update_dict.update({"department_ids": [(6, 0, department_ids)]})

        # print("update_dict", callback_employee, update_dict)

        if cmd == "create":
            # print("执行创建员工")
            update_dict.update(
                {"company_id": company_id.id, "is_wecom_user": True,}
            )
            try:
                wecomapi = self.env["wecom.service_api"].InitServiceApi(
                    company_id.corpid, company_id.contacts_app_id.secret
                )
                response = wecomapi.httpCall(
                    self.env["wecom.service_api_list"].get_server_api_call("USER_GET"),
                    {"userid": update_dict["wecom_userid"]},
                )
                if response.get("errcode") == 0:
                    update_dict.update({"qr_code": response.get("qr_code")})
            except:
                pass

            callback_employee.create(update_dict)
        elif cmd == "update":
            if "wecom_userid" in update_dict:
                del update_dict["wecom_userid"]
            # print("执行更新员工", update_dict)
            callback_employee.write(update_dict)
        elif cmd == "delete":
            # print("执行删除员工")
            callback_employee.write(
                {"active": False,}
            )

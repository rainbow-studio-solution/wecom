# -*- coding: utf-8 -*-

import logging
import time
from odoo import fields, models, api, _
from lxml import etree
from lxml_to_dict import lxml_to_dict
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException

_logger = logging.getLogger(__name__)


WECOM_USER_MAPPING_ODOO_PARTNER = {
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


class Users(models.Model):
    _inherit = "res.users"

    # ------------------------------------------------------------
    # 企微部门下载
    # ------------------------------------------------------------
    @api.model
    def download_wecom_contacts(self):
        """
        下载企微通讯录
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
                    self.env["wecom.service_api_list"].get_server_api_call("USER_LIST"),
                    {
                        "department_id": contacts_sync_hr_department_id,
                        "fetch_child": "1",
                    },
                )
            except ApiException as ex:
                end_time = time.time()
                self.env["wecomapi.tools.action"].ApiExceptionDialog(
                    ex, raise_exception=False
                )
                tasks = [
                    {
                        "name": "download_contact_data",
                        "state": False,
                        "time": end_time - start_time,
                        "msg": str(ex),
                    }
                ]
            except Exception as e:
                end_time = time.time()
                tasks = [
                    {
                        "name": "download_contact_data",
                        "state": False,
                        "time": end_time - start_time,
                        "msg": str(e),
                    }
                ]
            else:
                wecom_users = response["userlist"]

                # 获取block
                blocks = (
                    self.env["wecom.contacts.block"]
                    .sudo()
                    .search([("company_id", "=", company.id),])
                )
                block_list = []

                # 生成 block_list
                if len(blocks) > 0:
                    for obj in blocks:
                        if obj.wecom_userid != None:
                            block_list.append(obj.wecom_userid)

                # 从 wecom_users 移除 block_list
                for b in block_list:
                    for item in wecom_users:
                        # userid不区分大小写
                        if item["userid"].lower() == b.lower():
                            wecom_users.remove(item)

                # 1. 下载联系人
                for wecom_user in wecom_users:
                    download_user_result = self.download_user(company, wecom_user)
                    if download_user_result:
                        tasks.append(download_user_result)  # 加入设置下载联系人失败结果

        else:
            end_time = time.time()
            tasks = [
                {
                    "name": "download_contact_data",
                    "state": False,
                    "time": end_time - start_time,
                    "msg": _(
                        "The current company does not identify the enterprise wechat organization. Please configure or switch the company."
                    ),
                }
            ]  # 返回失败结果

        return tasks

    def download_user(self, company, wecom_user):
        """
        下载联系人
        """
        user = self.sudo().search(
            [
                ("wecom_userid", "=", wecom_user["userid"]),
                ("company_id", "=", company.id),
                ("is_wecom_user", "=", True),
                "|",
                ("active", "=", True),
                ("active", "=", False),
            ],
            limit=1,
        )
        result = {}
        app_config = self.env["wecom.app_config"].sudo()
        contacts_task_sync_user_enabled = app_config.get_param(
            company.contacts_app_id.id, "contacts_task_sync_user_enabled"
        )  # 允许创建用户
        if not user and contacts_task_sync_user_enabled:
            result = self.create_user(company, user, wecom_user)
        else:
            result = self.update_user(company, user, wecom_user)
        return result

    def create_user(self, company, user, wecom_user):
        """
        创建联系人
        """
        params = self.env["ir.config_parameter"].sudo()
        debug = params.get_param("wecom.debug_enabled")

        app_config = self.env["wecom.app_config"].sudo()
        contacts_use_system_default_avatar = app_config.get_param(
            company.contacts_app_id.id, "contacts_use_system_default_avatar"
        )  # 使用系统微信默认头像的标识
        if contacts_use_system_default_avatar == "True":
            contacts_use_system_default_avatar = True
        else:
            contacts_use_system_default_avatar = False
        try:
            groups_id = (
                self.sudo().env["res.groups"].search([("id", "=", 9),], limit=1,).id
            )  # id=1是内部用户, id=9是门户用户
            user.create(
                {
                    "company_ids": [(6, 0, [self.company_id.id])],
                    "company_id": self.company_id.id,
                    "name": wecom_user["name"],
                    "login": wecom_user["userid"].lower(),  # 登陆账号 使用 企业微信用户id的小写
                    "password": self.env["wecom.tools"].random_passwd(8),
                    "email": wecom_user["email"],
                    "work_phone": wecom_user["telephone"],
                    "mobile_phone": wecom_user["mobile"],
                    "employee_phone": wecom_user["mobile"],
                    "work_email": wecom_user["email"],
                    "gender": self.env["wecom.tools"].sex2gender(wecom_user["gender"]),
                    "wecom_userid": wecom_user["userid"].lower(),
                    "image_1920": self.env["wecomapi.tools.file"].get_avatar_base64(
                        contacts_use_system_default_avatar,
                        wecom_user["gender"],
                        wecom_user["avatar"],
                    ),
                    "qr_code": wecom_user["qr_code"],
                    "active": True if wecom_user["status"] == 1 else False,
                    "is_wecom_user": True,
                    "is_company": False,
                    "share": False,
                    "groups_id": [(6, 0, [groups_id])],  # 设置用户为门户用户
                    "tz": "Asia/Shanghai",
                    "lang": "zh_CN",
                }
            )
        except Exception as e:
            result = _("Error creating company %s partner %s %s, error reason: %s") % (
                company.name,
                wecom_user["userid"],
                wecom_user["name"],
                repr(e),
            )
            if debug:
                _logger.warning(result)
            return {
                "name": "add_partner",
                "state": False,
                "time": 0,
                "msg": result,
            }  # 返回失败结果

    def update_partner(self, company, user, wecom_user):
        """
        更新联系人
        """
        params = self.env["ir.config_parameter"].sudo()
        debug = params.get_param("wecom.debug_enabled")
        app_config = self.env["wecom.app_config"].sudo()
        contacts_use_system_default_avatar = app_config.get_param(
            company.contacts_app_id.id, "contacts_use_system_default_avatar"
        )  # 使用系统微信默认头像的标识
        if contacts_use_system_default_avatar == "True":
            contacts_use_system_default_avatar = True
        else:
            contacts_use_system_default_avatar = False
        try:
            user.write(
                {
                    "company_ids": [(6, 0, [self.company_id.id])],
                    "company_id": self.company_id.id,
                    "name": wecom_user["name"],
                    "login": wecom_user["userid"].lower(),  # 登陆账号 使用 企业微信用户id的小写
                    "email": wecom_user["email"],
                    "work_phone": wecom_user["telephone"],
                    "mobile_phone": wecom_user["mobile"],
                    "employee_phone": wecom_user["mobile"],
                    "work_email": wecom_user["email"],
                    "gender": self.env["wecom.tools"].sex2gender(wecom_user["gender"]),
                    "wecom_userid": wecom_user["userid"].lower(),
                    "image_1920": self.env["wecomapi.tools.file"].get_avatar_base64(
                        contacts_use_system_default_avatar,
                        wecom_user["gender"],
                        wecom_user["avatar"],
                    ),
                    "qr_code": wecom_user["qr_code"],
                    "active": True if wecom_user["status"] == 1 else False,
                }
            )
        except Exception as e:
            result = _("Error creating company %s partner %s %s, error reason: %s") % (
                company.name,
                wecom_user["userid"],
                wecom_user["name"],
                repr(e),
            )
            if debug:
                _logger.warning(result)
            return {
                "name": "update_partner",
                "state": False,
                "time": 0,
                "msg": result,
            }  # 返回失败结果

    # ------------------------------------------------------------
    # 企微通讯录事件
    # ------------------------------------------------------------
    def wecom_event_change_contact_partner(self, cmd):
        xml_tree = self.env.context.get("xml_tree")
        company_id = self.env.context.get("company_id")
        xml_tree_str = etree.fromstring(bytes.decode(xml_tree))
        dic = lxml_to_dict(xml_tree_str)["xml"]

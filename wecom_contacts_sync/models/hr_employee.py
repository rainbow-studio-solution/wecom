# -*- coding: utf-8 -*-

from odoo import api, models, _
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException

import logging
import time

_logger = logging.getLogger(__name__)

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def create_user_from_employee(self):
        """
        从员工生成用户
        :return:
        """
        groups_id = (
            self.sudo().env["res.groups"].search([("id", "=", 9),], limit=1,).id
        )  # id=1是内部用户, id=9是门户用户
        try:
            res_user_id = (
                self.sudo()
                .env["res.users"]
                .search([("login", "=", self.wecom_userid.lower())], limit=1,)
            )

            if len(res_user_id) == 0:
                res_user_id.create(
                    {
                        "notification_type": "inbox",
                        #
                        "employee_ids": [(6, 0, [self.id])],
                        "employee_id": self.id,
                        "company_ids": [(6, 0, [self.company_id.id])],
                        "company_id": self.company_id.id,
                        "name": self.name,
                        "login": self.wecom_userid.lower(),  # 登陆账号 使用 企业微信用户id的小写
                        "password": self.env["wecom.tools"].random_passwd(8),
                        "email": self.work_email,
                        "private_email": self.address_home_id.email,
                        "job_title": self.job_title,
                        "work_phone": self.work_phone,
                        "mobile_phone": self.mobile_phone,
                        "employee_phone": self.work_email,
                        "work_email": self.phone,
                        "category_ids": self.category_ids,
                        "department_id": self.department_id,
                        "gender": self.gender,
                        "wecom_userid": self.wecom_userid,
                        "image_1920": self.image_1920,
                        "qr_code": self.qr_code,
                        "active": self.active,
                        "wecom_user_order": self.wecom_user_order,
                        "is_wecom_user": True,
                        "is_moderator": False,
                        "is_company": False,
                        "employee": True,
                        "share": False,
                        "groups_id": [(6, 0, [groups_id])],  # 设置用户为门户用户
                        "tz": "Asia/Shanghai",
                        "lang": "zh_CN",
                    }
                )

        except Exception as e:
            _logger.warning(
                _("Generate system user error from employee. Error details:%s")
                % (repr(e))
            )
        else:
            self._sync_user(
                self.env["res.users"].browse(res_user_id), bool(self.image_1920)
            )

    # -------------------------------------------------------
    # 同步人员
    # -------------------------------------------------------
    def sync_employee(self, company):
        res = {}
        start_time = time.time()
        state = None

        params = self.env["ir.config_parameter"].sudo()
        debug = params.get_param("wecom.debug_enabled")
        if debug:
            _logger.info(_("Start synchronizing employees of '%s'"), company.name)
        try:
            app_config = self.env["wecom.app_config"].sudo()
            contacts_sync_hr_department_id = app_config.get_param(
                company.contacts_app_id.id, "contacts_sync_hr_department_id"
            )  # 需要同步的企业微信部门ID
            wxapi = self.env["wecom.service_api"].InitServiceApi(
                company.corpid, company.contacts_app_id.secret
            )
            response = wxapi.httpCall(
                self.env["wecom.service_api_list"].get_server_api_call("USER_LIST"),
                {"department_id": contacts_sync_hr_department_id, "fetch_child": "1",},
            )
            
        except ApiException as e:
            state = "fail"
            result = _("Error synchronizing employees of company: %s, error reason: %s") % (company.name, e.errMsg,)
            if debug:
                _logger.warning(
                   result
                )
        else:
            user_list = response["userlist"]

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
                        # block_list.append({"userid": obj.wecom_userid})
                        block_list.append(obj.wecom_userid)

            # 从user_list移除block
            for b in block_list:
                for item in user_list:
                    # userid不区分大小写
                    if item["userid"].lower() == b.lower():
                        user_list.remove(item)

            # 同步
            for obj in user_list:
                self.run_sync(company, obj)
  

            # 设置直属上级
            employees = (
                self.env["hr.employee"]
                .sudo()
                .search(
                    [
                        ("is_wecom_user", "=", True),
                        ("company_id", "=", company.id),
                        "|",
                        ("active", "=", True),
                        ("active", "=", False),
                    ],
                )
            )

            self.set_direct_leader(company, user_list)

            # 判断企业微信员工list为空，为空跳过同步离职员工
            if not employees:
                pass
            else:
                self.sync_leave_employee(company, response)  # 同步离职员工


            state = "completed"
            result = _("Successfully synchronized '%s''s WeCom users") % company.name
        finally:
            end_time = time.time()
            if debug:
                _logger.info(
                    _(
                        "End synchronizing employees of company %s,Total time spent: %s seconds"
                    )
                    % (company.name, end_time-start_time)
                )

            res.update({
                "employee_sync_times":end_time-start_time,
                "employee_sync_state":state,
                "employee_sync_result":result,
                })
            return res

    def run_sync(self, company, obj):
        params = self.env["ir.config_parameter"].sudo()
        debug = params.get_param("wecom.debug_enabled")

        employee = (
            self.env["hr.employee"]
            .sudo()
            .search(
                [
                    ("wecom_userid", "=", obj["userid"]),
                    ("company_id", "=", company.id),
                    ("is_wecom_user", "=", True),
                    "|",
                    ("active", "=", True),
                    ("active", "=", False),
                ],
                limit=1,
            )
        )

        try:
            if not employee:
                self.create_employee(company, employee, obj)
            else:
                self.update_employee(company, employee, obj)
        except Exception as e:
            if debug:
                _logger.warning(
                    _("Failed to synchronize company %s employee %s %s, error: %s")
                    % (company.name, obj["userid"], obj["name"], repr(e))
                )

    def create_employee(self, company, records, obj):
        params = self.env["ir.config_parameter"].sudo()
        debug = params.get_param("wecom.debug_enabled")
        department_ids = []  # 多部门
        if len(obj["department"]) > 0:
            department_ids = self.get_employee_parent_wecom_department(
                company, obj["department"]
            )

        try:
            app_config = self.env["wecom.app_config"].sudo()
            contacts_use_system_default_avatar = app_config.get_param(
                company.contacts_app_id.id, "contacts_use_system_default_avatar"
            )  # 使用系统微信默认头像的标识

            if contacts_use_system_default_avatar == "True":
                contacts_use_system_default_avatar = True
            else:
                contacts_use_system_default_avatar = False

            records.create(
                {
                    "wecom_userid": obj["userid"],
                    "name": obj["name"],
                    "english_name": self.env["wecom.tools"].check_dictionary_keywords(
                        obj, "english_name"
                    ),
                    "gender": self.env["wecom.tools"].sex2gender(obj["gender"]),
                    "marital": None,  # 不生成婚姻状况
                    "image_1920": self.env["wecomapi.tools.file"].get_avatar_base64(
                        contacts_use_system_default_avatar,
                        obj["gender"],
                        obj["avatar"],
                    ),
                    "mobile_phone": obj["mobile"],
                    "work_phone": obj["telephone"],
                    "work_email": obj["email"],
                    "active": True if obj["status"] == 1 else False,
                    "alias": obj["alias"],
                    "department_id": self.get_main_department(
                        company, obj["name"], obj["main_department"], department_ids
                    ),
                    "company_id": company.id,
                    "department_ids": [(6, 0, department_ids)],
                    "wecom_user_order": obj["order"],
                    "qr_code": obj["qr_code"],
                    "is_wecom_user": True,
                }
            )
            # result = True
        except Exception as e:
            if debug:
                _logger.warning(
                    _("Error creating company %s employee %s %s, error reason: %s")
                    % (company.name, obj["userid"], obj["name"], repr(e))
                )

    def update_employee(self, company, records, obj):
        params = self.env["ir.config_parameter"].sudo()
        debug = params.get_param("wecom.debug_enabled")
        department_ids = []  # 多部门

        if len(obj["department"]) > 0:
            department_ids = self.get_employee_parent_wecom_department(
                company, obj["department"]
            )

        try:
            records.write(
                {
                    "name": obj["name"],
                    "english_name": self.env["wecom.tools"].check_dictionary_keywords(
                        obj, "english_name"
                    ),
                    "mobile_phone": obj["mobile"],
                    "work_phone": obj["telephone"],
                    "work_email": obj["email"],
                    "active": True if obj["status"] == 1 else False,
                    "alias": obj["alias"],
                    "department_id": self.get_main_department(
                        company, obj["name"], obj["main_department"], department_ids
                    ),
                    "company_id": company.id,
                    "department_ids": [(6, 0, department_ids)],
                    "wecom_user_order": obj["order"],
                    "qr_code": obj["qr_code"],
                    "is_wecom_user": True,
                }
            )
            app_config = self.env["wecom.app_config"].sudo()
            contacts_update_avatar_every_time_sync = app_config.get_param(
                company.contacts_app_id.id, "contacts_update_avatar_every_time_sync"
            )  # 每次同步都更新头像的标识

            if contacts_update_avatar_every_time_sync == "True":
                contacts_update_avatar_every_time_sync = True
            else:
                contacts_update_avatar_every_time_sync = False
            if contacts_update_avatar_every_time_sync:
                records.write(
                    {
                        "image_1920": self.env["wecomapi.tools.file"].get_avatar_base64(
                            False, obj["gender"], obj["avatar"],
                        ),
                    }
                )
        except Exception as e:
            if debug:
                _logger.warning(
                    _("Error update company %s employee %s %s, error reason: %s")
                    % (company.name, obj["userid"], obj["name"], repr(e))
                )

    def get_employee_parent_wecom_department(self, company, departments):
        department_ids = []
        for department in departments:
            if department == 1:
                pass
            else:
                odoo_department = (
                    self.env["hr.department"]
                    .sudo()
                    .search(
                        [
                            ("wecom_department_id", "=", department),
                            ("company_id", "=", company.id),
                            ("is_wecom_department", "=", True),
                        ],
                        limit=1,
                    )
                )

                if len(odoo_department) > 0:
                    department_ids.append(odoo_department.id)
        return department_ids

    def get_main_department(self, company, employee_name, main_department, departments):
        """
        获取员工的主部门
        """
        params = self.env["ir.config_parameter"].sudo()
        debug = params.get_param("wecom.debug_enabled")
        if main_department == 1 and len(departments) > 1:
            for index, department in enumerate(departments):
                if department == 1:
                    del departments[index]
            main_department = departments[0]
        elif main_department == 1:
            return None

        try:
            departments = (
                self.env["hr.department"]
                .sudo()
                .search(
                    [
                        ("wecom_department_id", "=", main_department),
                        ("company_id", "=", company.id),
                        ("is_wecom_department", "=", True),
                    ],
                    limit=1,
                )
            )
            if len(departments) > 0:
                return departments.id
            else:
                return None

        except BaseException as e:
            if debug:
                _logger.warning(
                    _(
                        "Get the main department error of the company %s employee %s. The wrong reason is: %s."
                    )
                    % (company.name, employee_name, repr(e))
                )
            return None

    def set_direct_leader(self, company, wecom_users):
        """
        设置 直属上级
        """
        params = self.env["ir.config_parameter"].sudo()
        debug = params.get_param("wecom.debug_enabled")
        if debug:
            _logger.info(
                _(
                    "Start setting the direct leader of the employee with the company name '%s'."
                ),
                company.name,
            )
        for user in wecom_users:
            if len(user["direct_leader"]) > 0:
                direct_leader = (
                    self.env["hr.employee"]
                    .sudo()
                    .search(
                        [
                            ("wecom_userid", "=", user["direct_leader"][0]),
                            ("company_id", "=", company.id),
                            ("is_wecom_user", "=", True),
                            "|",
                            ("active", "=", True),
                            ("active", "=", False),
                        ],
                    )
                )

                employee = (
                    self.env["hr.employee"]
                    .sudo()
                    .search(
                        [
                            ("wecom_userid", "=", user["userid"]),
                            ("company_id", "=", company.id),
                            ("is_wecom_user", "=", True),
                            "|",
                            ("active", "=", True),
                            ("active", "=", False),
                        ],
                        limit=1,
                    )
                )
                employee.write({"parent_id": direct_leader.id})
            else:
                pass
        if debug:
            _logger.info(
                _(
                    "End setting the direct leader of the employee with the company name '%s'."
                ),
                company.name,
            )

    def sync_leave_employee(self, company, response):
        """
        比较企业微信和odoo的员工数据，且设置离职odoo员工active状态
        激活状态: 1=已激活，2=已禁用，4=未激活，5=退出企业。
        已激活代表已激活企业微信或已关注微工作台（原企业号）。未激活代表既未激活企业微信又未关注微工作台（原企业号）。
        TODO:待重构
        """
        params = self.env["ir.config_parameter"].sudo()
        debug = params.get_param("wecom.debug_enabled")
        try:
            list_user = []
            list_employee = []
            for wecom_employee in response["userlist"]:
                list_user.append(wecom_employee["userid"])

            domain = ["|", ("active", "=", False), ("active", "=", True)]
            employees = (
                self.env["hr.employee"]
                .sudo()
                .search(
                    domain
                    + [("is_wecom_user", "=", True), ("company_id", "=", company.id),]
                )
            )
            for employee in employees:
                list_employee.append(employee.wecom_userid)

            list_user_leave = list(
                set(list_employee).difference(set(list_user))
            )  # 生成odoo与企微不同的员工数据列表
            for wecom_leave_employee in list_user_leave:
                leave_employee = (
                    self.env["hr.employee"]
                    .sudo()
                    .search(
                        [
                            ("wecom_userid", "=", wecom_leave_employee),
                            ("company_id", "=", company.id),
                        ]
                    )
                )
                self.set_employee_active(leave_employee)
        except Exception as e:
            if debug:
                _logger.warning(
                    _("Errors in generating data for departing employees:%s")
                    % (repr(e))
                )

    def set_employee_active(self, records):
        params = self.env["ir.config_parameter"].sudo()
        debug = params.get_param("wecom.debug_enabled")
        try:
            records.write(
                {"active": False,}
            )
            # return True
        except Exception as e:
            if debug:
                _logger.warning(
                    _("Departed employee: %s, Synchronization error: %s ")
                    % (records.name, repr(e))
                )

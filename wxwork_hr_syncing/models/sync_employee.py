# -*- coding: utf-8 -*-

from odoo import api, models, modules, _

# from odoo.modules.module import get_module_resource

from odoo.addons.wxwork_api.api.corp_api import CorpApi, CORP_API_TYPE


import base64
import os
import logging
import platform
import time

_logger = logging.getLogger(__name__)


class SyncEmployee(object):
    def __init__(self, kwargs):
        self.kwargs = kwargs

        self.debug = self.kwargs["debug"]
        self.img_path = self.kwargs["img_path"]

        self.company = self.kwargs["company"]
        self.corpid = self.kwargs["company"].corpid
        self.secret = self.kwargs["company"].contacts_secret
        self.sync_hr = self.kwargs["company"].contacts_auto_sync_hr_enabled
        self.use_default_avatar = self.kwargs[
            "company"
        ].contacts_use_system_default_avatar  # 使用系统默认头像

        self.department_id = self.kwargs[
            "company"
        ].contacts_sync_hr_department_id  # 需要同步的部门ID

        self.department = self.kwargs["department"]
        self.employee = self.kwargs["employee"]
        self.employee_category = self.kwargs["employee_category"]
        self.wx_tools = self.kwargs["wx_tools"]

    def run(self):
        """[summary]
        运行同步
        """
        if self.debug:
            _logger.info(_("Start synchronizing employees of %s"), self.company.name)

        try:
            api = CorpApi(self.corpid, self.secret)
            response = api.httpCall(
                CORP_API_TYPE["USER_LIST"],
                {"department_id": str(self.department_id), "fetch_child": "1",},
            )
            start1 = time.time()
            for obj in response["userlist"]:
                self.run_sync(obj)
            end1 = time.time()

            times1 = end1 - start1

            # 判断企业微信员工list为空，为空跳过同步离职员工
            start2 = time.time()
            employees = self.employee.sudo().search(
                [
                    ("is_wxwork_employee", "=", True),
                    ("company_id", "=", self.company.id),
                    "|",
                    ("active", "=", True),
                    ("active", "=", False),
                ],
            )
            if not employees:
                pass
            else:
                self.sync_leave_employee(response)  # 同步离职员工

            end2 = time.time()
            times2 = end2 - start2
            times = times1 + times2
            # status = {"employee": True}
            result = _("Successfully synchronize employees of %s") % self.company.name
        except BaseException as e:
            times = time.time()
            result = _("Failed to synchronize employees of %s") % self.company.name

            if self.debug:
                print(
                    _("Error synchronizing employees of company: %s, error reason: %s")
                    % (self.company.name, repr(e))
                )
        if self.debug:
            _logger.info(
                _(
                    "End synchronizing employees of company %s,Total time spent: %s seconds"
                )
                % (self.company.name, times)
            )

        return times, result

    def run_sync(self, obj):
        employee = self.employee.sudo().search(
            [
                ("wxwork_id", "=", obj["userid"]),
                ("company_id", "=", self.company.id),
                ("is_wxwork_employee", "=", True),
                "|",
                ("active", "=", True),
                ("active", "=", False),
            ],
            limit=1,
        )

        try:
            if not employee:
                self.create_employee(employee, obj)
            else:
                self.update_employee(employee, obj)
        except Exception as e:
            if self.debug:
                print(
                    _("Failed to synchronize company %s employee %s %s, error: %s")
                    % (self.company.name, obj["userid"], obj["name"], repr(e))
                )

    def create_employee(self, records, obj):
        department_ids = []  # 多部门
        if len(obj["department"]) > 0:
            department_ids = self.get_employee_parent_wxwork_department(
                obj["department"]
            )

        try:
            records.create(
                {
                    "use_system_avatar": self.use_default_avatar,
                    "wxwork_id": obj["userid"],
                    "name": obj["name"],
                    "english_name": self.wx_tools.check_dictionary_keywords(
                        obj, "english_name"
                    ),
                    "gender": self.wx_tools.sex2gender(obj["gender"]),
                    "marital": None,  # 不生成婚姻状况
                    "avatar": self.wx_tools.get_default_avatar_url(obj["gender"])
                    if obj["avatar"] == ""
                    else obj["avatar"],
                    "image_1920": self.wx_tools.encode_avatar_image_as_base64(
                        obj["gender"]
                    ),
                    "mobile_phone": obj["mobile"],
                    "work_phone": obj["telephone"],
                    "work_email": obj["email"],
                    "active": obj["enable"],
                    "alias": obj["alias"],
                    "department_id": self.get_main_department(
                        obj["name"], obj["main_department"], department_ids
                    ),
                    "company_id": self.company.id,
                    "department_ids": [(6, 0, department_ids)],
                    "wxwork_user_order": obj["order"],
                    "qr_code": obj["qr_code"],
                    "is_wxwork_employee": True,
                }
            )
            # result = True
        except Exception as e:
            if self.debug:
                print(
                    _("Error creating company %s employee %s %s, error reason: %s")
                    % (self.company.name, obj["userid"], obj["name"], repr(e))
                )
        # result = False
        # return result

    def update_employee(self, records, obj):
        department_ids = []  # 多部门
        if len(obj["department"]) > 0:
            department_ids = self.get_employee_parent_wxwork_department(
                obj["department"]
            )

        try:
            records.write(
                {
                    "use_system_avatar": self.use_default_avatar,
                    "name": obj["name"],
                    "english_name": self.wx_tools.check_dictionary_keywords(
                        obj, "english_name"
                    ),
                    "avatar": self.wx_tools.get_default_avatar_url(obj["gender"])
                    if obj["avatar"] == ""
                    else obj["avatar"],
                    "mobile_phone": obj["mobile"],
                    "work_phone": obj["telephone"],
                    "work_email": obj["email"],
                    "active": obj["enable"],
                    "alias": obj["alias"],
                    "department_id": self.get_main_department(
                        obj["name"], obj["main_department"], department_ids
                    ),
                    "company_id": self.company.id,
                    "department_ids": [(6, 0, department_ids)],
                    "wxwork_user_order": obj["order"],
                    "qr_code": obj["qr_code"],
                    "is_wxwork_employee": True,
                }
            )

        except Exception as e:
            if self.debug:
                print(
                    _("Error update company %s employee %s %s, error reason: %s")
                    % (self.company.name, obj["userid"], obj["name"], repr(e))
                )

    def check_always_update_avatar(self, always, gender, avatar_file, employee):
        if always:
            return self.wx_tools.encode_avatar_image_as_base64(gender, avatar_file)
        else:
            return employee.image_1920

    # def encode_image_as_base64(self, image_path):
    #     try:
    #         with open(image_path, "rb") as f:
    #             encoded_string = base64.b64encode(f.read())
    #         return encoded_string
    #     except BaseException as e:
    #         print(_("Image encoding error:" + repr(e)))

    def get_employee_parent_hr_department(self, department_obj):
        """
        如果企微用户只有一个部门，则设置企业用户的HR部门
        :param department_obj: 部门json
        :return:
            企微用户只有一个部门，返回department_id
            企微用户归属多个部门，返回 None
        """
        try:
            departments = self.department.sudo().search(
                [
                    ("wxwork_department_id", "in", department_obj),
                    ("company_id", "=", self.company.id),
                    ("is_wxwork_department", "=", True),
                ],
                limit=1,
            )
            if departments:
                return departments.id
        except BaseException as e:
            if self.debug:
                print(
                    _("Error in getting employee's parent department, error: %s")
                    % repr(e)
                )

    def get_employee_parent_wxwork_department(self, departments):
        department_ids = []
        for department in departments:
            if department == 1:
                pass
            else:
                odoo_department = self.department.sudo().search(
                    [
                        ("wxwork_department_id", "=", department),
                        ("company_id", "=", self.company.id),
                        ("is_wxwork_department", "=", True),
                    ],
                    limit=1,
                )

                if len(odoo_department) > 0:
                    department_ids.append(odoo_department.id)
        return department_ids

    def get_main_department(self, employee_name, main_department, departments):
        """
        获取员工的主部门
        """

        if main_department == 1 and len(departments) > 1:
            for index, department in enumerate(departments):
                if department == 1:
                    del departments[index]
            main_department = departments[0]
        elif main_department == 1:
            return None

        try:
            departments = self.department.sudo().search(
                [
                    ("wxwork_department_id", "=", main_department),
                    ("company_id", "=", self.company.id),
                    ("is_wxwork_department", "=", True),
                ],
                limit=1,
            )
            if len(departments) > 0:
                return departments.id
            else:
                return None

        except BaseException as e:
            if self.debug:
                print(
                    _(
                        "Get the main department error of the company %s employee %s. The wrong reason is: %s."
                    )
                    % (self.company.name, employee_name, repr(e))
                )
            return None

    def sync_leave_employee(self, response):
        """
        比较企业微信和odoo的员工数据，且设置离职odoo员工active状态
        激活状态: 1=已激活，2=已禁用，4=未激活，5=退出企业。
        已激活代表已激活企业微信或已关注微工作台（原企业号）。未激活代表既未激活企业微信又未关注微工作台（原企业号）。
        TODO:待重构
        """
        try:
            list_user = []
            list_employee = []
            for wxwork_employee in response["userlist"]:
                list_user.append(wxwork_employee["userid"])

            domain = ["|", ("active", "=", False), ("active", "=", True)]
            employees = self.employee.sudo().search(
                domain
                + [
                    ("is_wxwork_employee", "=", True),
                    ("company_id", "=", self.company.id),
                ]
            )
            for employee in employees:
                list_employee.append(employee.wxwork_id)

            list_user_leave = list(
                set(list_employee).difference(set(list_user))
            )  # 生成odoo与企微不同的员工数据列表
            for wxwork_leave_employee in list_user_leave:
                leave_employee = self.employee.sudo().search(
                    [
                        ("wxwork_id", "=", wxwork_leave_employee),
                        ("company_id", "=", self.company.id),
                    ]
                )
                self.set_employee_active(leave_employee)
        except Exception as e:
            if self.debug:
                print(
                    _("Errors in generating data for departing employees:%s")
                    % (repr(e))
                )

    def set_employee_active(self, records):
        try:
            records.write(
                {"active": False,}
            )
            # return True
        except Exception as e:
            if self.debug:
                print(
                    _("Departed employee: %s, Synchronization error: %s ")
                    % (records.name, repr(e))
                )


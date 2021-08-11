# -*- coding: utf-8 -*-

from odoo import api, models, _
from odoo.modules.module import get_module_resource

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
        self.corpid = self.kwargs["corpid"]
        self.secret = self.kwargs["secret"]
        self.debug = self.kwargs["debug"]
        self.img_path = self.kwargs["img_path"]
        self.sync_hr = self.kwargs["sync_hr"]
        self.sync_avatar = self.kwargs["sync_avatar"]
        self.always_sync_avatar = self.kwargs["always_sync_avatar"]
        self.company = self.kwargs["company"]
        self.department = self.kwargs["department"]
        self.department_id = self.kwargs["department_id"]
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
            employees = self.search(
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
            result = (
                _("Successfully synchronize employees of company %s"),
                self.company.name,
            )
        except BaseException as e:
            times = time.time()
            result = _("Failed to synchronize employees of %s"), self.company.name

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
                    _("Failed to synchronize company %s employee %s, error: %s")
                    % (self.company.name, obj["name"], repr(e))
                )

    def create_employee(self, records, obj):
        department_ids = []  # 多部门
        for department in obj["department"]:
            department_ids.append(
                self.get_employee_parent_wxwork_department(obj, department)
            )
        print("部门", type(obj["department"]), obj["department"], department_ids)
        img_path = self.img_path
        if platform.system() == "Windows":
            avatar_file = (
                img_path.replace("\\", "/")
                + str(self.company.id)
                + "/avatar/"
                + obj["userid"]
                + ".jpg"
            )
            qr_code_file = (
                img_path.replace("\\", "/")
                + str(self.company.id)
                + "/qr_code/"
                + obj["userid"]
                + ".png"
            )
        else:
            avatar_file = (
                img_path + str(self.company.id) + "/avatar/" + obj["userid"] + ".jpg"
            )
            qr_code_file = (
                img_path + str(self.company.id) + "/qr_code/" + obj["userid"] + ".png"
            )

        try:
            records.create(
                {
                    "wxwork_id": obj["userid"],
                    "name": obj["name"],
                    "english_name": self.wx_tools.check_dictionary_keywords(
                        obj, "english_name"
                    ),
                    "gender": self.wx_tools.gender(obj["gender"]),
                    "marital": None,  # 不生成婚姻状况
                    "image_1920": self.encode_avatar_image_as_base64(
                        obj["gender"], avatar_file
                    ),
                    "mobile_phone": obj["mobile"],
                    "work_phone": obj["telephone"],
                    "work_email": obj["email"],
                    "active": obj["enable"],
                    "alias": obj["alias"],
                    # 归属多个部门的情况下，第一个部门为默认部门 obj["main_department"]
                    # "department_id": department_ids[0],
                    "department_id": self.get_main_department(
                        obj["name"], obj["main_department"]
                    ),
                    "company_id": self.company.id,
                    "department_ids": [(6, 0, department_ids)],
                    "wxwork_user_order": obj["order"],
                    "qr_code": self.encode_image_as_base64(qr_code_file),
                    "is_wxwork_employee": True,
                }
            )
            # result = True
        except Exception as e:
            if self.debug:
                print(
                    _("Error creating company %s employee %s, error reason: %s")
                    % (self.company.name, obj["name"], repr(e))
                )
            # result = False
        # return result

    def update_employee(self, records, obj):
        always = self.always_sync_avatar

        department_ids = []
        for department in obj["department"]:
            department_ids.append(
                self.get_employee_parent_wxwork_department(obj, department)
            )

        img_path = self.img_path
        if platform.system() == "Windows":
            avatar_file = (
                img_path.replace("\\", "/")
                + str(self.company.id)
                + "/avatar/"
                + obj["userid"]
                + ".jpg"
            )
            qr_code_file = (
                img_path.replace("\\", "/")
                + str(self.company.id)
                + "/qr_code/"
                + obj["userid"]
                + ".png"
            )
        else:
            avatar_file = (
                img_path + str(self.company.id) + "/avatar/" + obj["userid"] + ".jpg"
            )
            qr_code_file = (
                img_path + str(self.company.id) + "/qr_code/" + obj["userid"] + ".png"
            )
        try:
            records.write(
                {
                    "name": obj["name"],
                    "english_name": self.wx_tools.check_dictionary_keywords(
                        obj, "english_name"
                    ),
                    "gender": self.wx_tools.gender(obj["gender"]),
                    "image_1920": self.check_always_update_avatar(
                        always, obj["gender"], avatar_file, records
                    ),
                    "mobile_phone": obj["mobile"],
                    "work_phone": obj["telephone"],
                    "work_email": obj["email"],
                    "active": obj["enable"],
                    "alias": obj["alias"],
                    # 归属多个部门的情况下，第一个部门为默认部门
                    # "department_id": department_ids[0],
                    "department_id": self.get_main_department(
                        obj["name"], obj["main_department"]
                    ),
                    "company_id": self.company.id,
                    "department_ids": [(6, 0, department_ids)],
                    "wxwork_user_order": obj["order"],
                    "qr_code": self.encode_image_as_base64(qr_code_file),
                    "is_wxwork_employee": True,
                }
            )

        except Exception as e:
            if self.debug:
                print(
                    _("Error update company %s employee %s, error reason: %s")
                    % (self.company.name, obj["name"], repr(e))
                )

    def check_always_update_avatar(self, always, gender, avatar_file, employee):
        if always:
            return self.encode_avatar_image_as_base64(gender, avatar_file)
        else:
            return employee.image_1920

    def encode_avatar_image_as_base64(self, gender, image_path):
        if not os.path.exists(image_path):
            if not gender:
                image_path = get_module_resource(
                    "wxwork_hr_syncing", "static/src/img", "default_image.png"
                )
            else:
                if gender == 1:
                    image_path = get_module_resource(
                        "wxwork_hr_syncing", "static/src/img", "default_male_image.png"
                    )
                elif gender == 2:
                    image_path = get_module_resource(
                        "wxwork_hr_syncing",
                        "static/src/img",
                        "default_female_image.png",
                    )
            return base64.b64encode(open(image_path, "rb").read())
        else:
            try:
                with open(image_path, "rb") as f:
                    encoded_string = base64.b64encode(f.read())
                return encoded_string
            except BaseException as e:
                print(_("Image encoding error:" + repr(e)))

    def encode_image_as_base64(self, image_path):
        try:
            with open(image_path, "rb") as f:
                encoded_string = base64.b64encode(f.read())
            return encoded_string
        except BaseException as e:
            print(_("Image encoding error:" + repr(e)))

    def get_employee_parent_hr_department(self, department_obj, debug):
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
                    ("is_wxwork_department", "=", True),
                ],
                limit=1,
            )
            if departments:
                return departments.id
        except BaseException as e:
            if debug:
                print(
                    _("Error in getting employee's parent department, error: %s")
                    % repr(e)
                )

    def get_employee_parent_wxwork_department(self, employee, department_id):
        try:
            departments = self.department.sudo().search(
                [
                    ("wxwork_department_id", "=", department_id),
                    ("company_id", "=", self.company.id),
                    ("is_wxwork_department", "=", True),
                ],
                limit=1,
            )
            print("获取上级部门", departments)
            if len(departments) > 0:
                return departments.id
        except BaseException as e:
            if self.debug:
                print(
                    _(
                        "Error getting parent department of employee %s of company %s, error reason: %s"
                    )
                    % (employee["name"], self.company.name, repr(e))
                )

    def get_main_department(self, employee_name, main_department):
        """
        获取员工的主部门
        """
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
        except BaseException as e:
            if self.debug:
                print(
                    _(
                        "Get the main department error of the company %s employee %s. The wrong reason is: %s."
                    )
                    % (self.company.name, employee_name, repr(e))
                )

    def sync_leave_employee(self, response, debug):
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
            employees = self.search(domain + [("is_wxwork_employee", "=", True)])
            for employee in employees:
                list_employee.append(employee.wxwork_id)

            list_user_leave = list(
                set(list_employee).difference(set(list_user))
            )  # 生成odoo与企微不同的员工数据列表
            for wxwork_leave_employee in list_user_leave:
                leave_employee = employees.search(
                    [("wxwork_id", "=", wxwork_leave_employee)]
                )
                self.set_employee_active(leave_employee, debug)
        except Exception as e:
            if debug:
                print(
                    _("Errors in generating data for departing employees:%s")
                    % (repr(e))
                )

    def set_employee_active(self, records, debug):
        try:
            records.write(
                {"active": False,}
            )
            # return True
        except Exception as e:
            if debug:
                print(
                    _("Departed employee: %s, Synchronization error: %s ")
                    % (records.name, repr(e))
                )


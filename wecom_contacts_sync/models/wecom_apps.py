# -*- coding: utf-8 -*-

import logging
import datetime
import re
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

from io import StringIO
import pandas as pd

pd.set_option("max_colwidth", 4096)  # 设置最大列宽
pd.set_option("display.max_columns", 30)  # 设置最大列数
pd.set_option("expand_frame_repr", False)  # 当列太多时不换行
import time

from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException

_logger = logging.getLogger(__name__)


class WeComApps(models.Model):
    _inherit = "wecom.apps"

    # ————————————————————————————————————
    # 应用回调服务
    # ————————————————————————————————————
    # def generate_service(self):
    #     """
    #     生成服务
    #     :return:
    #     """
    #     params = self.env["ir.config_parameter"].sudo()
    #     base_url = params.get_param("web.base.url")
    #     if not self.app_id:
    #         raise ValidationError(_("Please bind contact app!"))
    #     else:
    #         self.callback_url = base_url + "/wecom_callback/%s/%s" % (
    #             self.app_id.company_id.id,
    #             self.code,
    #         )

    def generate_service_by_code(self, code):
        """
        根据code生成回调服务
        :param code:
        :return:
        """
        if code == "contacts":
            service = self.app_callback_service_ids.sudo().search(
                [
                    ("app_id", "=", self.id),
                    ("code", "=", code),
                    "|",
                    ("active", "=", True),
                    ("active", "=", False),
                ]
            )

            if not service:
                service.create(
                    {
                        "app_id": self.id,
                        "name": _("Contacts synchronization"),
                        "code": code,
                        "callback_url_token": "",
                        "callback_aeskey": "",
                        "description": _(
                            "When members modify their personal information, the modified information will be pushed to the following URL in the form of events to ensure the synchronization of the address book."
                        ),
                    }
                )
            else:
                service.write(
                    {
                        "name": _("Contacts synchronization"),
                        "code": code,
                        "callback_url": service.generate_service(),
                        "description": _(
                            "When members modify their personal information, the modified information will be pushed to the following URL in the form of events to ensure the synchronization of the address book."
                        ),
                    }
                )

    # ————————————————————————————————————
    # 应用参数配置
    # ————————————————————————————————————

    def generate_parameters_by_code(self, code):
        """
        根据code生成参数
        :param code:
        :return:
        注意：14使用 get_object_reference 方法，15 没有此方法，
        故在 \wecom_base\models\ir_model.py 添加了 get_object_reference方法
        """
        if code == "contacts":
            # 从xml 获取数据
            ir_model_data = self.env["ir.model.data"]
            contacts_allow_sync_hr = ir_model_data.get_object_reference(
                "wecom_contacts_sync", "wecom_app_config_contacts_allow_sync_hr"
            )[
                1
            ]  # 1
            contacts_sync_hr_department_id = ir_model_data.get_object_reference(
                "wecom_contacts_sync", "wecom_app_config_contacts_sync_hr_department_id"
            )[
                1
            ]  # 2
            contacts_edit_enabled = ir_model_data.get_object_reference(
                "wecom_contacts_sync", "wecom_app_config_contacts_edit_enabled"
            )[
                1
            ]  # 3
            contacts_allow_add_system_users = ir_model_data.get_object_reference(
                "wecom_contacts_sync",
                "wecom_app_config_contacts_allow_add_system_users",
            )[
                1
            ]  # 4
            contacts_use_default_avatar_when_adding_employees = ir_model_data.get_object_reference(
                "wecom_contacts_sync",
                "wecom_app_config_contacts_use_default_avatar_when_adding_employees",
            )[
                1
            ]  # 5
            contacts_update_avatar_every_time_sync_employees = (
                ir_model_data.get_object_reference(
                    "wecom_contacts_sync",
                    "wecom_app_config_contacts_update_avatar_every_time_sync_employees",
                )[1]
            )  # 6
            # enabled_join_qrcode = ir_model_data.get_object_reference(
            #     "wecom_contacts_sync", "wecom_app_config_contacts_enabled_join_qrcode"
            # )[
            #     1
            # ]  # 7
            # join_qrcode = ir_model_data.get_object_reference(
            #     "wecom_contacts_sync", "wecom_app_config_contacts_join_qrcode"
            # )[
            #     1
            # ]  # 8
            # join_qrcode_size_type = ir_model_data.get_object_reference(
            #     "wecom_contacts_sync", "wecom_app_config_contacts_join_qrcode_size_type"
            # )[
            #     1
            # ]  # 9
            # join_qrcode_last_time = ir_model_data.get_object_reference(
            #     "wecom_contacts_sync",
            #     "wecom_app_config_acontacts_join_qrcode_last_time",
            # )[
            #     1
            # ]  # 10

            vals_list = [
                contacts_allow_sync_hr,  # 1
                contacts_sync_hr_department_id,  # 2
                contacts_edit_enabled,  # 3
                contacts_allow_add_system_users,  # 4
                contacts_use_default_avatar_when_adding_employees,  # 5
                contacts_update_avatar_every_time_sync_employees,  # 6
                # enabled_join_qrcode,  # 7
                # join_qrcode,  # 8
                # join_qrcode_size_type,  # 9
                # join_qrcode_last_time,  # 10
            ]

            for id in vals_list:
                app_config_id = self.env["wecom.app_config"].search([("id", "=", id)])
                app_config = (
                    self.env["wecom.app_config"]
                    .sudo()
                    .search([("app_id", "=", self.id), ("key", "=", app_config_id.key)])
                )

                if not app_config:
                    app_config.sudo().create(
                        {
                            "name": app_config_id.name,
                            "app_id": self.id,
                            "key": app_config_id.key,
                            "ttype": app_config_id.ttype,
                            "value": ""
                            if app_config_id.key == "join_qrcode"
                            or app_config_id.key == "join_qrcode_last_time"
                            else app_config_id.value,
                            "description": app_config_id.description,
                        }
                    )
                else:
                    app_config.sudo().write(
                        {
                            "name": app_config_id.name,
                            "description": app_config_id.description,
                        }
                    )

        super(WeComApps, self).generate_parameters_by_code(code)

    # ————————————————————————————————————
    # 通讯录
    # ————————————————————————————————————

    def cron_sync_contacts(self):
        """
        自动任务同步组织架构
        同步内容:    1. wecom.department
                    2. wecom.user
                    3. wecom.tag
        """
        results = []
        total_time = 0
        sync_start_time = time.time()

        for app in self.search(
            [("company_id", "!=", False), ("type_code", "=", "['contacts']")]
        ):
            _logger.info(
                _(
                    "Automatic task: start to synchronize the enterprise wechat organizational structure of the company [%s]"
                )
                % (app.company_id.name)
            )

            result = app.sync_contacts()
            results.append(result)

            _logger.info(
                _(
                    "Automatic task: end synchronizing the enterprise wechat organizational structure of the company [%s]"
                )
                % (app.company_id.name)
            )
        df = pd.DataFrame(results)

        (
            sync_task_state,
            wecom_department_sync_state,
            wecom_user_sync_state,
            wecom_tag_sync_state,
        ) = self.handle_sync_all_state(
            df
        )  # 处理同步状态

        # 处理同步结果和时间
        sync_task_result = ""
        wecom_department_sync_result = ""
        wecom_user_sync_result = ""
        wecom_tag_sync_result = ""

        wecom_department_sync_times = 0
        wecom_user_sync_times = 0
        wecom_tag_sync_times = 0

        rows = len(df)  # 获取所有行数

        for index, row in df.iterrows():
            if row["sync_state"] == "fail":
                sync_task_result += self.handle_sync_result(
                    index, rows, row["sync_result"]
                )

            wecom_department_sync_result += self.handle_sync_result(
                index, rows, row["wecom_department_sync_result"]
            )
            wecom_user_sync_result += self.handle_sync_result(
                index, rows, row["wecom_user_sync_result"]
            )
            wecom_tag_sync_result += self.handle_sync_result(
                index, rows, row["wecom_tag_sync_result"]
            )

            wecom_department_sync_times += row["wecom_department_sync_times"]
            wecom_user_sync_times += row["wecom_user_sync_times"]
            wecom_tag_sync_times += row["wecom_tag_sync_times"]

        sync_end_time = time.time()
        total_time = sync_end_time - sync_start_time
        _logger.info(
            _(
                """
Automatic task: end the synchronization of the enterprise wechat organizational structure of all companies.
=======================================================================================================================
Task Synchronization status:%s, Synchronization task time:%s seconds,
Synchronization results：
%s
-----------------------------------------------------------------------------------------------------------------------
Wecom department sync status:%s, Synchronize Wecom department time: %s seconds,
Synchronize Wecom department results:
%s
-----------------------------------------------------------------------------------------------------------------------
Wecom User sync status:%s, Synchronize Wecom User time: %s seconds,
Synchronize Wecom User results:
%s
-----------------------------------------------------------------------------------------------------------------------
Wecom tag sync status:%s, Synchronize Wecom tag time: %s seconds,
Synchronize Wecom tag results:
%s
======================================================================================================================="""
            )
            % (
                # 任务
                self.get_state_name(sync_task_state),
                total_time,
                sync_task_result,
                # 企微部门
                self.get_state_name(wecom_department_sync_state),
                wecom_department_sync_times,
                wecom_department_sync_result,
                # 企微员工
                self.get_state_name(wecom_user_sync_state),
                wecom_user_sync_times,
                wecom_user_sync_result,
                # 企微标签
                self.get_state_name(wecom_tag_sync_state),
                wecom_tag_sync_times,
                wecom_tag_sync_result,
            )
        )

    def sync_contacts(self):
        """
        同步通讯录
        """
        # result = {
            
        # }

        result = {
            "company_name": self.company_id.name, 
            "sync_state": "completed",

            "wecom_department_sync_state": "fail",
            "wecom_department_sync_times": 0,
            "wecom_department_sync_result": "",

            "wecom_user_sync_state": "fail",
            "wecom_user_sync_times": 0,
            "wecom_user_sync_result": "",

            "wecom_tag_sync_state": "fail",
            "wecom_tag_sync_times": 0,
            "wecom_tag_sync_result": "",
        }

        # 同步企微部门
        sync_department_result = (
            self.env["wecom.department"]
            .with_context(company_id=self.company_id)
            .download_wecom_deps()
        )

        (
            wecom_department_sync_state,
            wecom_department_sync_times,
            wecom_department_sync_result,
        ) = self.handle_sync_task_state(sync_department_result, self.company_id)

        result.update(
            {
                "wecom_department_sync_state": wecom_department_sync_state,
                "wecom_department_sync_times": wecom_department_sync_times,
                "wecom_department_sync_result": wecom_department_sync_result,
            }
        )

        if result["wecom_department_sync_state"] == "fail":
            return result

        # 同步企微用户
        sync_user_result = (
            self.env["wecom.user"]
            .with_context(company_id=self.company_id)
            .download_wecom_users()
        )
        (
            wecom_user_sync_state,
            wecom_user_sync_times,
            wecom_user_sync_result,
        ) = self.handle_sync_task_state(sync_user_result, self.company_id)
        result.update(
            {
                "wecom_user_sync_state": wecom_user_sync_state,
                "wecom_user_sync_times": wecom_user_sync_times,
                "wecom_user_sync_result": wecom_user_sync_result,
            }
        )

        if result["wecom_user_sync_state"] == "fail":
            return result

        # 同步企微标签
        sync_wecom_tag_result = (
            self.env["wecom.tag"]
            .with_context(company_id=self.company_id)
            .download_wecom_tags()
        )
        (
            wecom_tag_sync_state,
            wecom_tag_sync_times,
            wecom_tag_sync_result,
        ) = self.handle_sync_task_state(sync_wecom_tag_result, self.company_id)
        result.update(
            {
                "wecom_tag_sync_state": wecom_tag_sync_state,
                "wecom_tag_sync_times": wecom_tag_sync_times,
                "wecom_tag_sync_result": wecom_tag_sync_result,
            }
        )

        if result["wecom_tag_sync_state"] == "fail":
            return result

        return result

    def get_state_name(self, key):
        """
        获取状态名称
        """
        STATE = {
            "completed": _("All completed"),
            "partially": _("Partially complete"),
            "fail": _("All failed"),
        }
        return dict(STATE).get(key, _("Unknown"))  # 如果没有找到，返回Unknown

    def handle_sync_result(self, index, rows, result):
        """
        处理同步结果
        """
        if result is None:
            return ""
        if index < rows - 1:
            result = "%s:%s \n" % (str(index + 1), result)
        else:
            result = "%s:%s" % (str(index + 1), result)
        return result

    def handle_sync_all_state(self, df):
        """
        处理同步状态
        """
        all_state_rows = len(df)  # 获取所有行数
        fail_state_rows = len(df[df["sync_state"] == "fail"])  # 获取失败行数

        # 获取部门失败行数
        fail_department_state_rows = len(
            df[df["wecom_department_sync_state"] == "fail"]
        )

        # 获取用户失败行数
        fail_user_state_rows = len(df[df["wecom_user_sync_state"] == "fail"])

        # 获取标签失败行数
        fail_tag_state_rows = len(df[df["wecom_tag_sync_state"] == "fail"])

        sync_state = None
        wecom_department_sync_state = None
        wecom_employee_sync_state = None
        wecom_tag_sync_state = None

        if fail_state_rows == all_state_rows:
            sync_state = "fail"
        elif fail_state_rows > 0 and fail_state_rows < all_state_rows:
            sync_state = "partially"
        elif fail_state_rows == 0:
            sync_state = "completed"

        # 部门
        if fail_department_state_rows == all_state_rows:
            wecom_department_sync_state = "fail"
        elif (
            fail_department_state_rows > 0
            and fail_department_state_rows < all_state_rows
        ):
            wecom_department_sync_state = "partially"
        elif fail_department_state_rows == 0:
            wecom_department_sync_state = "completed"

        # 员工
        if fail_user_state_rows == all_state_rows:
            wecom_user_sync_state = "fail"
        elif fail_user_state_rows > 0 and fail_user_state_rows < all_state_rows:
            wecom_user_sync_state = "partially"
        elif fail_user_state_rows == 0:
            wecom_user_sync_state = "completed"

        if fail_tag_state_rows == all_state_rows:
            wecom_tag_sync_state = "fail"
        elif fail_tag_state_rows > 0 and fail_tag_state_rows < all_state_rows:
            wecom_tag_sync_state = "partially"
        elif fail_tag_state_rows == 0:
            wecom_tag_sync_state = "completed"

        return (
            sync_state,
            wecom_department_sync_state,
            wecom_user_sync_state,
            wecom_tag_sync_state,
        )

    def handle_sync_task_state(self, result, company):
        """
        处理部门、用户、标签的 同步状态
        """
        df = pd.DataFrame(result)
        all_rows = len(df)  # 获取所有行数
        fail_rows = len(df[df["state"] == False])  # 获取失败行数

        sync_state = None
        if fail_rows == all_rows:
            sync_state = "fail"
        elif fail_rows > 0 and fail_rows < all_rows:
            sync_state = "partially"
        elif fail_rows == 0:
            sync_state = "completed"

        sync_result = ""
        sync_times = 0
        for index, row in df.iterrows():
            sync_times += row["time"]
            sync_result += "[%s] %s" % (company.name, row["msg"])

        return sync_state, sync_times, sync_result

# -*- coding: utf-8 -*-

import logging
import datetime
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from ..api.wecom_abstract_api import ApiException

_logger = logging.getLogger(__name__)


class WeComApps(models.Model):
    _inherit = "wecom.apps"

    # 回调服务
    app_callback_service_ids = fields.One2many(
        "wecom.app_callback_service",
        "app_id",
        string="Receive event service",
        domain="['|', ('active', '=', True), ('active', '=', False)]",
        context={"active_test": False},
    )

    # 应用参数配置
    app_config_ids = fields.One2many(
        "wecom.app_config",
        "app_id",
        string="Application Configuration",
        # context={
        #     "default_company_id": lambda self: self.company_id,
        # },
    )  # 应用参数配置

    # ————————————————————————————————————
    # 应用回调服务
    # ————————————————————————————————————
    def generate_service(self):
        """
        生成回调服务
        :return:
        """
        code = self.env.context.get("code")  # 按钮的传递值
        if bool(code):
            # 存在按钮的传递值，通过按钮的传递值生成回调服务
            self.generate_service_by_code(code)
        else:
            # 不存在按钮的传递值，通过子类型生成生成回调服务
            self.generate_service_by_subtype()

    def generate_service_by_subtype(self):
        """
        通过子类型生成生成回调服务
        """
        for record in self.subtype_ids:
            self.generate_service_by_code(record.code)

    def generate_service_by_code(self, code):
        """
        根据code生成回调服务
        :param code:
        :return:
        """
        # ("app_id", "in", self.id),
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
    def generate_parameters(self):
        """
        生成参数
        :return:
        """
        code = self.env.context.get("code")  # 按钮的传递值
        if bool(code):
            # 存在按钮的传递值，通过按钮的传递值生成回调服务
            self.generate_parameters_by_code(code)
        else:
            # 不存在按钮的传递值，通过子类型生成生成回调服务
            self.generate_parameters_by_subtype()

    def generate_parameters_by_subtype(self):
        """
        通过子类型生成生成参数
        """
        for record in self.subtype_ids:
            self.generate_parameters_by_code(record.code)

    def generate_parameters_by_code(self, code):
        """
        根据code生成参数
        :param code:
        :return:
        """
        if code == "contacts":
            # 从xml 获取数据
            ir_model_data = self.env["ir.model.data"]
            contacts_auto_sync_hr_enabled = ir_model_data.get_object_reference(
                "wecom_base", "wecom_app_config_contacts_auto_sync_hr_enabled"
            )[
                1
            ]  # 1
            contacts_sync_hr_department_id = ir_model_data.get_object_reference(
                "wecom_base", "wecom_app_config_contacts_sync_hr_department_id"
            )[
                1
            ]  # 2
            contacts_edit_enabled = ir_model_data.get_object_reference(
                "wecom_base", "wecom_app_config_contacts_edit_enabled"
            )[
                1
            ]  # 3
            contacts_sync_user_enabled = ir_model_data.get_object_reference(
                "wecom_base", "wecom_app_config_contacts_sync_user_enabled"
            )[
                1
            ]  # 4
            contacts_use_system_default_avatar = ir_model_data.get_object_reference(
                "wecom_base", "wecom_app_config_contacts_use_system_default_avatar"
            )[
                1
            ]  # 5
            contacts_update_avatar_every_time_sync = ir_model_data.get_object_reference(
                "wecom_base", "wecom_app_config_contacts_update_avatar_every_time_sync"
            )[
                1
            ]  # 6
            enabled_join_qrcode = ir_model_data.get_object_reference(
                "wecom_base", "wecom_app_config_contacts_enabled_join_qrcode"
            )[
                1
            ]  # 7
            join_qrcode = ir_model_data.get_object_reference(
                "wecom_base", "wecom_app_config_contacts_join_qrcode"
            )[
                1
            ]  # 8
            join_qrcode_size_type = ir_model_data.get_object_reference(
                "wecom_base", "wecom_app_config_contacts_join_qrcode_size_type"
            )[
                1
            ]  # 9
            join_qrcode_last_time = ir_model_data.get_object_reference(
                "wecom_base", "wecom_app_config_acontacts_join_qrcode_last_time"
            )[
                1
            ]  # 10

            vals_list = [
                contacts_auto_sync_hr_enabled,  # 1
                contacts_sync_hr_department_id,  # 2
                contacts_edit_enabled,  # 3
                contacts_sync_user_enabled,  # 4
                contacts_use_system_default_avatar,  # 5
                contacts_update_avatar_every_time_sync,  # 6
                enabled_join_qrcode,  # 7
                join_qrcode,  # 8
                join_qrcode_size_type,  # 9
                join_qrcode_last_time,  # 10
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

    # ————————————————————————————————————
    # 应用信息
    # ————————————————————————————————————

    def get_app_info(self):
        """
        获取企业应用信息
        :param agentid:
        :return:
        """
        for record in self:
            try:
                wecomapi = self.env["wecom.service_api"].InitServiceApi(
                    record.company_id.corpid, record.secret
                )
                response = wecomapi.httpCall(
                    self.env["wecom.service_api_list"].get_server_api_call("AGENT_GET"),
                    {"agentid": str(record.agentid)},
                )
            except ApiException as e:
                return self.env["wecomapi.tools.action"].ApiExceptionDialog(
                    e, raise_exception=True
                )
            else:
                if response["errcode"] == 0:
                    record.write(
                        {
                            "app_name": response["name"],
                            "square_logo_url": response["square_logo_url"],
                            "description": response["description"],
                            "allow_userinfos": response["allow_userinfos"]
                            if "allow_userinfos" in response
                            else "{}",
                            "allow_partys": response["allow_partys"]
                            if "allow_partys" in response
                            else "{}",
                            "allow_tags": response["allow_tags"]
                            if "allow_tags" in response
                            else "{}",
                            "close": response["close"],
                            "redirect_domain": response["redirect_domain"],
                            "report_location_flag": response["report_location_flag"],
                            "isreportenter": response["isreportenter"],
                            "home_url": response["home_url"],
                        }
                    )
                    # msg = {
                    #     "title": _("Tips"),
                    #     "message": _("Successfully obtained application information!"),
                    #     "sticky": False,
                    # }
                    # return self.env["wecomapi.tools.action"].WecomSuccessNotification(msg)

    def set_app_info(self):
        """
        设置企业应用信息
        :param agentid:
        :return:
        """

    # ————————————————————————————————————
    # 应用令牌
    # ————————————————————————————————————
    def get_access_token(self):
        """获取企业应用接口调用凭据（令牌）
        :return:
        """
        ir_config = self.env["ir.config_parameter"].sudo()
        debug = ir_config.get_param("wecom.debug_enabled")
        if debug:
            _logger.info(_("Start getting token for app [%s]") % (self.name))
        try:
            wecom_api = self.env["wecom.service_api"].InitServiceApi(
                self.company_id.corpid, self.secret
            )

        except ApiException as ex:
            return self.env["wecomapi.tools.action"].ApiExceptionDialog(
                ex, raise_exception=True
            )
        # finally:
        #     if self.expiration_time and self.expiration_time > datetime.now():
        #         # 令牌未过期，则直接返回 提示信息
        #         msg = {
        #             "title": _("Tips"),
        #             "message": _("Token is still valid, and no update is required!"),
        #             "sticky": False,
        #         }
        #         return self.env["wecomapi.tools.action"].WecomInfoNotification(msg)

    def cron_get_app_token(self):
        """
        自动任务定时获取应用token
        """
        for app in self.search([("company_id", "!=", False)]):
            _logger.info(
                _("Automatic task:Start getting token for app [%s].") % (app.name)
            )
            app.get_access_token()

    # ————————————————————————————————————
    # 通讯录
    # ————————————————————————————————————
    def get_join_qrcode(self):
        """
        获取加入企业二维码
        :return:
        """
        ir_config = self.env["ir.config_parameter"].sudo()
        debug = ir_config.get_param("wecom.debug_enabled")
        if debug:
            _logger.info(
                _("Start getting join enterprise QR code for app [%s]") % (self.name)
            )

        if self.subtype_ids.code == "contacts":
            if len(self.app_config_ids) == 0:
                raise UserError(_("Please generate application parameters first."))

            try:
                wecomapi = self.env["wecom.service_api"].InitServiceApi(
                    self.company_id.corpid, self.secret
                )
                app_config = self.env["wecom.app_config"].sudo()
                size_type = app_config.get_param(self.id, "join_qrcode_size_type")

                # qrcode = self.app_config_ids.sudo().search(
                #     [("key", "=", "join_qrcode")], limit=1
                # )

                # last_time = self.app_config_ids.sudo().search(
                #     [("key", "=", "join_qrcode_last_time")], limit=1
                # )
                # print(self.company_id.name, qrcode, size_type, last_time)
                response = wecomapi.httpCall(
                    self.env["wecom.service_api_list"].get_server_api_call(
                        "GET_JOIN_QRCODE"
                    ),
                    {"size_type": size_type},
                )
                if response["errcode"] == 0:
                    app_config.set_param(
                        self.id, "join_qrcode", response["join_qrcode"]
                    )
                    app_config.set_param(
                        self.id,
                        "join_qrcode_last_time",
                        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    )
                    # qrcode.write({"value": response["join_qrcode"]})
                    # last_time.write(
                    #     {"value": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                    # )

            except ApiException as ex:
                return self.env["wecomapi.tools.action"].ApiExceptionDialog(
                    ex, raise_exception=True
                )

    def cron_get_join_qrcode(self):
        """
        自动任务获取加入企业二维码
        """
        _logger.info(_("Automatic task:Start to get join enterprise QR code."))
        for app in self.search(
            [("company_id", "!=", False), ("type_code", "=", "['contacts']")]
        ):
            app.get_join_qrcode()

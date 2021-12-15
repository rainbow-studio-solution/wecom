# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from typing_extensions import Required
from odoo import _, api, fields, models
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException


CONTACTS_PARAMETERS = [
    {
        "name": _("Allow WeCom Contacts are automatically updated to HR"),
        "key": "contacts_auto_sync_hr_enabled",
        "value": "True",
        "description": _(
            "If enabled, it allows to read the WeCom address book through the API interface and automatically synchronize to ODOO;<br></br>Otherwise, you can only manually bind WeCom users."
        ),
    },
    {
        "name": _("Department ID to be synchronized"),
        "key": "contacts_sync_hr_department_id",
        "value": "1",
        "description": _(
            "Department id. Get the specified department and its sub-departments. If you don’t fill in, get the full organization structure by default"
        ),
    },
    {
        "name": _("Allow API to edit WeCom contacts"),
        "key": "contacts_edit_enabled",
        "value": "False",
        "description": "",
    },
    {
        "name": _("Allow WeCom contacts to automatically update system accounts"),
        "key": "contacts_sync_user_enabled",
        "value": "1",
        "description": _(
            "Enable to allow batch generation of system accounts from employees;"
        ),
    },
    {
        "name": _("Use system default Avatar"),
        "key": "contacts_use_system_default_avatar",
        "value": "True",
        "description": _(
            "Enable this, Employee photos will use the default avatar. Will save a lot of synchronization time.<hr></hr><span class='text-info font-weight-bold'>Valid only when synchronizing new employees.</span>"
        ),
    },
    {
        "name": _("Update avatar every time sync"),
        "key": "contacts_update_avatar_every_time_sync",
        "value": "True",
        "description": _(
            "Enable this,Each update will overwrite the employee photos you have set up.<hr></hr><span class='text-warning font-weight-bold'>Use this feature with caution.</span>"
        ),
    },
]

MANAGE_APP_TYPE = [
    ("msgaudit", _("Session content archiving")),
    ("contacts", _("Contacts synchronization")),
]

BASE_APP_TYPE = [
    ("calendar", _("Calendar")),
    ("meeting", _("Meeting")),
    ("dial", _("Public telephone")),
    ("wedrive", _("We Drive")),
    ("living", _("Living")),
    ("checkin", _("Checkin")),
    ("approval", _("Approval")),
    ("journal", _("Journal")),
    ("meetingroom", _("Meeting room")),
    ("health", _("Health")),
    ("externalpay", _("External pay")),
    ("kf", _("Wechat customer service")),
    ("enterprisepay", _("Enterprise pay")),
]


class WeComApps(models.Model):
    _inherit = "wecom.apps"

    # 应用类型  required=True
    type = fields.Selection(
        [
            ("manage", "Manage Tools"),
            ("base", "Base application"),
            ("self", "Self built application"),
            ("third", "Third party application"),
        ],
        string="Application Type",
        required=True,
        copy=True,
    )

    subtype = fields.Selection(
        compute="_compute_subtype",
        selection=lambda self: self._selection_values(),
        string="Application Subtype",
    )

    def _selection_values(self):
        return MANAGE_APP_TYPE + BASE_APP_TYPE

    @api.depends("type")
    def _compute_subtype(self):
        for res in self:
            if res.type == "manage":
                res.subtype.selection = MANAGE_APP_TYPE
            elif res.type == "base":
                res.subtype.selection = BASE_APP_TYPE

    # @api.onchange("type")
    # def _onchange_type(self):
    #     self.subtype = False

    #     if self.type:
    #         print(self.type)
    #         if self.type == "manage":
    #             self.subtype.selection = MANAGE_APP_TYPE
    #         elif self.type == "base":
    #             self.subtype.selection = BASE_APP_TYPE
    #     return {
    #         "domain": {"app_subtype_id": [("parent_id", "=", self.app_type_id.id)]}
    #     }
    # else:
    #     return {"domain": {"app_subtype_id": []}}

    # app_type_id = fields.Many2one(
    #     "wecom.app.type",
    #     string="Type",
    # )
    # app_subtype_id = fields.Many2one("wecom.app.subtype", string="Subtype")

    # @api.onchange("app_type_id")
    # def _onchange_app_type_id(self):
    #     self.app_subtype_id = False

    #     if self.app_type_id:
    #         return {
    #             "domain": {"app_subtype_id": [("parent_id", "=", self.app_type_id.id)]}
    #         }
    #     else:
    #         return {"domain": {"app_subtype_id": []}}

    # 回调服务
    app_callback_service_ids = fields.One2many(
        "wecom.app_callback_service",
        "app_id",
        string="Receive event service",
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

    def generate_service(self):
        """
        生成回调服务
        :return:
        """
        code = self.env.context.get("code")
        if bool(code) and code == "contacts":
            # 创建通讯录回调服务
            app_callback_service = (
                self.env["wecom.app_callback_service"]
                .sudo()
                .search([("app_id", "=", self.id), ("code", "=", code)])
            )
            if not app_callback_service:
                app_callback_service.create(
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
                app_callback_service.write(
                    {
                        "name": _("Contacts synchronization"),
                        "code": code,
                        "description": _(
                            "When members modify their personal information, the modified information will be pushed to the following URL in the form of events to ensure the synchronization of the address book."
                        ),
                    }
                )

    def generate_parameters(self):
        """
        生成通讯录参数
        :return:
        """
        code = self.env.context.get("code")
        if bool(code) and code == "contacts":
            for prame in CONTACTS_PARAMETERS:
                app_config = (
                    self.env["wecom.app_config"]
                    .sudo()
                    .search([("app_id", "=", self.id), ("key", "=", prame["key"])])
                )

                if not app_config:
                    app_config = (
                        self.env["wecom.app_config"]
                        .sudo()
                        .create(
                            {
                                "name": prame["name"],
                                "app_id": self.id,
                                "key": prame["key"],
                                "value": prame["value"],
                                "description": prame["description"],
                            }
                        )
                    )
                else:
                    app_config.write(
                        {
                            "name": prame["name"],
                            "value": prame["value"],
                            "description": prame["description"],
                        }
                    )

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
                    # return self.env["wecomapi.tools.action"].ApiSuccessNotification(msg)

    def set_app_info(self):
        """
        设置企业应用信息
        :param agentid:
        :return:
        """

    def get_access_token(self):
        """获取企业应用接口调用凭据（令牌）
        :return:
        """
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
        #         return self.env["wecomapi.tools.action"].ApiInfoNotification(msg)

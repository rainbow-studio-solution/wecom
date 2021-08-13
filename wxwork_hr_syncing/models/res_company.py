# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError

# from ..models.hr_employee import EmployeeSyncUser
from ..models.sync_contacts import *
from odoo.addons.wxwork_api.api.corp_api import CorpApi, CORP_API_TYPE
from odoo.addons.wxwork_api.api.abstract_api import ApiException
from odoo.addons.wxwork_api.api.error_code import Errcode

import logging

_logger = logging.getLogger(__name__)


class Company(models.Model):
    _inherit = "res.company"

    def get_contacts_access_token(self):
        ir_config = self.env["ir.config_parameter"].sudo()
        corpid = self.corpid
        secret = self.contacts_secret
        # debug = ir_config.get_param("wxwork.debug_enabled")
        if corpid == False:
            raise UserError(_("Please fill in correctly Enterprise ID."))
        elif (
            "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" in secret
            or self.contacts_secret == False
        ):
            raise UserError(_("Please fill in the contact Secret correctly."))
        else:
            params = {}
            wxapi = CorpApi(corpid, secret)
            try:
                response = wxapi.httpCall(
                    CORP_API_TYPE["GET_ACCESS_TOKEN"],
                    {"corpid": corpid, "corpsecret": secret,},
                )
                if "errcode" in str(response):
                    if response["errcode"] == 0:
                        params = {
                            "title": _("Success"),
                            "message": _(
                                "Successfully obtained corporate WeChat contact token."
                            ),
                            "sticky": False,  # 延时关闭
                            "className": "bg-success",
                            "next": {
                                "type": "ir.actions.client",
                                "tag": "reload",
                            },  # 刷新窗体
                        }

                        self.contacts_access_token = wxapi.getAccessToken()

                        action = {
                            "type": "ir.actions.client",
                            "tag": "display_notification",
                            "params": {
                                "title": params["title"],
                                "type": "success",
                                "message": params["message"],
                                "sticky": params["sticky"],
                                "next": params["next"],
                            },
                        }
                        return action
                else:
                    raise UserError(_("Please fill in the contact Secret correctly."))

            except ApiException as ex:
                params = {
                    "title": _("Failed"),
                    "message": _(
                        "Error code: %s "
                        + "\n"
                        + "Error description: %s"
                        + "\n"
                        + "Error Details:"
                        + "\n"
                        + "%s"
                    )
                    % (str(ex.errCode), Errcode.getErrcode(ex.errCode), ex.errMsg),
                    "sticky": True,  # 不会延时关闭，需要手动关闭
                    "next": {},
                }
                action = {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        # "className": "wxwork_config_notification",
                        "title": params["title"],
                        "type": "danger",
                        "message": params["message"],
                        "sticky": params["sticky"],  # 不会延时关闭，需要手动关闭
                        "next": params["next"],
                    },
                }
                return action

    # def cron_sync_contacts(self):
    #     """
    #     同步通讯录任务
    #     :return:
    #     """
    #     params = self.env["ir.config_parameter"].sudo()
    #     kwargs = {
    #         "corpid": params.get_param("wxwork.corpid"),
    #         "secret": params.get_param("wxwork.contacts_secret"),
    #         "debug": params.get_param("wxwork.debug_enabled"),
    #         "department_id": params.get_param("wxwork.contacts_sync_hr_department_id"),
    #         "sync_hr": params.get_param("wxwork.contacts_auto_sync_hr_enabled"),
    #         "img_path": params.get_param("wxwork.img_path"),
    #         "department": self.env["hr.department"],
    #         "department_category": self.env["hr.department.category"],
    #         "employee": self.env["hr.employee"],
    #         "employee_category": self.env["hr.employee.category"],
    #     }

    #     try:
    #         SyncTask(kwargs).run()
    #     except Exception as e:
    #         if params.get_param("wxwork.debug_enabled"):
    #             _logger.warning(
    #                 _(
    #                     "Task failure prompt - The task of synchronizing Enterprise WeChat contacts on a regular basis cannot be executed. The detailed reasons are as follows:%s"
    #                     % (e)
    #                 )
    #             )

    # def cron_sync_users(self):
    #     """
    #         同步系统用户任务
    #         :return:
    #         """
    #     params = self.env["ir.config_parameter"].sudo()

    #     if not params.get_param("wxwork.contacts_sync_user_enabled"):
    #         if params.get_param("wxwork.debug_enabled"):
    #             _logger.warning(
    #                 _(
    #                     "The current setting does not allow synchronization from employees to system users"
    #                 )
    #             )
    #         raise UserError(
    #             "The current setting does not allow synchronization from employees to system users \n\n Please check related settings"
    #         )
    #     else:
    #         try:
    #             EmployeeSyncUser.sync_user(self.env["hr.employee"])
    #         except Exception as e:
    #             if params.get_param("wxwork.debug_enabled"):
    #                 _logger.warning(
    #                     _(
    #                         "Task Failure Prompt - It is impossible to perform the task of synchronizing corporate WeChat employees as system users. The detailed reasons are as follows:%s"
    #                         % (e)
    #                     )
    #                 )

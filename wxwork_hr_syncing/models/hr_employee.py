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


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def update_from_enterprise_wechat(self):
        pass

    def create_user_from_employee(self):
        """
        从员工生成用户
        :return:
        """
        groups_id = (
            self.sudo().env["res.groups"].search([("id", "=", 9),], limit=1,).id
        )  # id=9是门户用户
        res_user_id = self.env["res.users"].create(
            {
                "name": self.name,
                "login": self.wxwork_id,
                # "oauth_uid": self.wxwork_id,
                "password": self.env["wxwork.tools"].random_passwd(8),
                "email": self.work_email,
                "wxwork_id": self.wxwork_id,
                "image_1920": self.image_1920,
                "qr_code": self.qr_code,
                "active": self.active,
                "wxwork_user_order": self.wxwork_user_order,
                "mobile": self.mobile_phone,
                "phone": self.work_phone,
                # "notification_type": "wxwork",
                "is_wxwork_user": True,
                "is_moderator": False,
                "is_company": False,
                "employee": True,
                "share": False,
                "company_id": self.company_id,
                "groups_id": [(6, 0, [groups_id])],  # 设置用户为门户用户
                "tz": "Asia/Chongqing",
                "lang": "zh_CN",
            }
        )
        self.user_id = res_user_id.id
        self.address_home_id = res_user_id.partner_id.id
        self.user_check_tick = True

    @api.onchange("address_home_id")
    def user_checking(self):
        if self.address_home_id:
            self.user_check_tick = True
        else:
            self.user_check_tick = False


# class EmployeeSyncUser(models.Model):
#     _inherit = "hr.employee"
#     _description = "Enterprise WeChat employees bind system users"

#     def sync_user(self):
#         params = self.env["ir.config_parameter"].sudo()
#         debug = params.get_param("wxwork.debug_enabled")

#         if debug:
#             _logger.info(_("Start syncing from employees to system users"))

#         domain = ["|", ("active", "=", False), ("active", "=", True)]
#         start = time.time()
#         try:
#             with api.Environment.manage():
#                 new_cr = self.pool.cursor()
#                 self = self.with_env(self.env(cr=new_cr))

#                 employees = (
#                     self.sudo()
#                     .env["hr.employee"]
#                     .search(
#                         domain
#                         + [
#                             ("is_wxwork_employee", "=", True),
#                             ("user_check_tick", "=", False),
#                         ]
#                     )
#                 )

#                 result = _(
#                     "There is currently no employee profile that needs to generate system users"
#                 )
#                 status = False
#                 for employee in employees:
#                     user = (
#                         self.sudo()
#                         .env["res.users"]
#                         .search(
#                             domain
#                             + [
#                                 ("wxwork_id", "=", employee.wxwork_id),
#                                 ("is_wxwork_user", "=", True),
#                             ],
#                             limit=1,
#                         )
#                     )

#                     try:
#                         if len(user) > 0:
#                             self.update_user(user, employee, debug)
#                         else:
#                             self.create_user(user, employee, debug)

#                         result = _(
#                             "Employee synchronization is successful as system user"
#                         )
#                         status = True
#                     except Exception as e:
#                         result = _("Failed to synchronize employee as system user")
#                         status = False
#                         if debug:
#                             print(
#                                 _("Failed to synchronize employee as system user:%s")
#                                 % (repr(e))
#                             )

#                 end = time.time()

#                 new_cr.commit()
#                 new_cr.close()
#                 times = end - start

#                 if debug:
#                     _logger.info(
#                         _(
#                             "Finished synchronizing enterprise WeChat contacts - employee synchronization system users, total time spent: %s seconds"
#                         )
#                         % times
#                     )
#         except BaseException as e:
#             if debug:
#                 _logger.info(
#                     _("Employee synchronization as system user error: %s") % (repr(e))
#                 )
#             result = _("Failed to synchronize employee as system user")
#             status = False

#         return times, status, result

#     def create_user(self, user, employee, debug):
#         try:
#             groups_id = (
#                 self.sudo().env["res.groups"].search([("id", "=", 9),], limit=1,).id
#             )  # id=9是门户用户
#             user = user.create(
#                 {
#                     "name": employee.name,
#                     "login": employee.wxwork_id,
#                     # "oauth_uid": employee.wxwork_id,
#                     "password": self.env["wxwork.tools"].random_passwd(8),  # 随机密码
#                     "email": employee.work_email,
#                     "wxwork_id": employee.wxwork_id,
#                     "image_1920": employee.image_1920,
#                     # 'qr_code': employee.qr_code,
#                     "active": employee.active,
#                     "wxwork_user_order": employee.wxwork_user_order,
#                     "mobile": employee.mobile_phone,
#                     "phone": employee.work_phone,
#                     "notification_type": "wxwork",
#                     "is_wxwork_user": True,
#                     "is_moderator": False,
#                     "is_company": False,
#                     "employee": True,
#                     "share": False,
#                     "groups_id": [(6, 0, [groups_id])],  # 设置用户为门户用户
#                     "tz": "Asia/Chongqing",
#                     "lang": "zh_CN",
#                 }
#             )

#             employee.write(
#                 {
#                     "user_id": user.id,
#                     "address_home_id": user.partner_id.id,
#                     "user_check_tick": True,
#                 }
#             )
#         except Exception as e:
#             if debug:
#                 print(_("Error creating system user from employee:%s") % (repr(e)))

#     def update_user(self, user, employee, debug):
#         try:
#             user.write(
#                 {
#                     "name": employee.name,
#                     # "oauth_uid": employee.wxwork_id,
#                     # 'email': employee.work_email,
#                     "image_1920": employee.image_1920,
#                     "wxwork_user_order": employee.wxwork_user_order,
#                     "is_wxwork_user": True,
#                     "mobile": employee.mobile_phone,
#                     "phone": employee.work_phone,
#                 }
#             )
#         except Exception as e:
#             if debug:
#                 print(_("Error creating system user from employee: %s") % (repr(e)))

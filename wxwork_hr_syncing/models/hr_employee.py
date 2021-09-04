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
        try:
            res_user_id = self.env["res.users"].create(
                {
                    "address_id": self.address_id,
                    "work_location": self.work_location,
                    "coach_id": self.coach_id,
                    "address_home_id": self.address_home_id,
                    "is_address_home_a_company": self.is_address_home_a_company,
                    "km_home_work": self.km_home_work,
                    #
                    "employee_ids": [(6, 0, [self.id])],
                    "company_ids": [(6, 0, [self.company_id.id])],
                    "company_id": self.company_id.id,
                    "name": self.name,
                    "login": self.wxwork_id,
                    "password": self.env["wxwork.tools"].random_passwd(8),
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
                    "wxwork_id": self.wxwork_id,
                    "image_1920": self.image_1920,
                    "qr_code": self.qr_code,
                    "active": self.active,
                    "wxwork_user_order": self.wxwork_user_order,
                    "is_wxwork_user": True,
                    "is_moderator": False,
                    "is_company": False,
                    "employee": True,
                    "share": False,
                    "groups_id": [(6, 0, [groups_id])],  # 设置用户为门户用户
                    "tz": "Asia/Shanghai",
                    "lang": "zh_CN",
                }
            )
            if res_user_id:

                res_user_id.partner_id.write(
                    {"company_id": self.company_id.id,}
                )
                self.write(
                    {
                        "user_id": res_user_id.id,
                        "user_partner_id": res_user_id.id,
                        "address_home_id": res_user_id.partner_id.id,
                    }
                )

        except Exception as e:
            print(
                _("Generate system user error from employee. Error details:%s")
                % (repr(e))
            )


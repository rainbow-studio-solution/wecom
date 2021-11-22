# -*- coding: utf-8 -*-

from odoo import api, models, _
from odoo.modules.module import get_module_resource
import time
import logging

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
            self.sudo()
            .env["res.groups"]
            .search(
                [
                    ("id", "=", 9),
                ],
                limit=1,
            )
            .id
        )  # id=9是门户用户
        try:
            res_user_id = (
                self.sudo()
                .env["res.users"]
                .search(
                    [("login", "=", self.wecom_id)],
                    limit=1,
                )
            )
            if not res_user_id:
                res_user_id.create(
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
                        "login": self.wecom_id,
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
                        "wecom_id": self.wecom_id,
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

            res_user_id.partner_id.write(
                {
                    "company_id": self.company_id.id,
                }
            )
            self.write(
                {
                    "user_id": res_user_id.id,
                    "user_partner_id": res_user_id.id,
                    "address_home_id": res_user_id.partner_id.id,
                }
            )

        except Exception as e:
            _logger.warning(
                _("Generate system user error from employee. Error details:%s")
                % (repr(e))
            )

    # --------------------------------------
    # 企业微信员工批量同步为系统用户
    # --------------------------------------
    def sync_as_user(self):
        """[summary]
        运行同步
        """
        start = time.time()
        results = ""
        result = ""
        params = self.env["ir.config_parameter"].sudo()
        debug = params.get_param("wecom.debug_enabled")
        if debug:
            _logger.info(_("Start batch generating system users from employees"))

        # 获取 标记为 企业微信组织 的公司
        companies = (
            self.sudo()
            .env["res.company"]
            .search([(("is_wecom_organization", "=", True))])
        )

        if not companies:
            action = {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Tips"),
                    "type": "info",
                    "message": _("There are currently no companies to synchronize."),
                    "sticky": False,
                },
            }
            return action

        for company in companies:
            if debug:
                _logger.info(
                    _("Company %s began to generate system users from employees")
                    % (company.name)
                )
            sync_user = company.contacts_sync_user_enabled

            if sync_user:
                if debug:
                    _logger.info(
                        _("Start generating system users from employees of company %s")
                        % company.name
                    )
                employees = (
                    self.sudo()
                    .env["hr.employee"]
                    .search(
                        [
                            "&",
                            "&",
                            ("company_id", "=", company.id),
                            ("is_wecom_employee", "=", True),
                            "|",
                            ("active", "=", False),
                            ("active", "=", True),
                        ]
                    )
                )

                for employee in employees:
                    user = (
                        self.sudo()
                        .env["res.users"]
                        .search(
                            [
                                "&",
                                "&",
                                ("wecom_id", "=", employee.wecom_id),
                                ("is_wecom_user", "=", True),
                                "|",
                                ("active", "=", False),
                                ("active", "=", True),
                            ],
                        )
                    )
                    try:
                        if len(user) > 0:
                            # 更新
                            self.update_user(user, employee, company)
                        else:
                            # 创建
                            self.create_user(user, employee, company)
                        result = _(
                            "Company %s successfully generated system user from employee."
                        ) % (company.name)
                    except Exception as e:
                        print(
                            _(
                                "Company %s failed to generate system user from employee. Failure reason:%s"
                            )
                            % (company.name, repr(e))
                        )
                        result = _(
                            "Company %s failed to generate system user from employee. Failure reason:%s"
                        ) % (company.name, repr(e))

                if debug:
                    _logger.info(
                        _("End generating system users from employees of company %s")
                        % (company.name)
                    )
            else:
                _logger.warning(
                    _("Company %s does not allow batch generation of system users")
                    % (company.name)
                )
                result = _(
                    "Company %s does not allow batch generation of system users"
                ) % (company.name)

            results += result + "\n"
        if debug:
            _logger.info(_("End batch generating system users from employees"))
        end = time.time()
        times = end - start

        return times, results

    def create_user(self, user, employee, company):
        params = self.env["ir.config_parameter"].sudo()
        debug = params.get_param("wecom.debug_enabled")
        groups_id = (
            self.sudo()
            .env["res.groups"]
            .search(
                [
                    ("id", "=", 9),
                ],
                limit=1,
            )
            .id
        )  # id=9是门户用户
        try:
            user = user.create(
                {
                    "address_id": employee.address_id,
                    "work_location": employee.work_location,
                    "coach_id": employee.coach_id,
                    "address_home_id": employee.address_home_id,
                    "is_address_home_a_company": employee.is_address_home_a_company,
                    "km_home_work": employee.km_home_work,
                    #
                    "employee_ids": [(6, 0, [employee.id])],
                    "company_ids": [(6, 0, [employee.company_id.id])],
                    "company_id": employee.company_id.id,
                    "name": employee.name,
                    "login": employee.wecom_id,
                    "password": self.env["wecom.tools"].random_passwd(8),
                    "email": employee.work_email,
                    "private_email": employee.address_home_id.email,
                    "job_title": employee.job_title,
                    "work_phone": employee.work_phone,
                    "mobile_phone": employee.mobile_phone,
                    "employee_phone": employee.work_email,
                    "work_email": employee.phone,
                    "category_ids": employee.category_ids,
                    "department_id": employee.department_id,
                    "gender": employee.gender,
                    "wecom_id": employee.wecom_id,
                    "image_1920": employee.image_1920,
                    "qr_code": employee.qr_code,
                    "active": employee.active,
                    "wecom_user_order": employee.wecom_user_order,
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
            if user.id:
                user.partner_id.write(
                    {
                        "company_id": employee.company_id.id,
                    }
                )
                employee.write(
                    {
                        "user_id": user.id,
                        "user_partner_id": user.id,
                        "address_home_id": user.partner_id.id,
                    }
                )
        except Exception as e:
            if debug:
                print(
                    _(
                        "System user error generated by employee %s of company %s. Error reason:%s"
                    )
                    % (employee.name, employee.company_id.name, repr(e))
                )

    def update_user(self, user, employee, company):
        params = self.env["ir.config_parameter"].sudo()
        debug = params.get_param("wecom.debug_enabled")

        user.write(
            {
                "name": employee.name,
                "image_1920": employee.image_1920,
                "is_wecom_user": True,
                "mobile": employee.mobile_phone,
                "phone": employee.work_phone,
            }
        )
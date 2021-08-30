# -*- coding: utf-8 -*-

from odoo import api, models, modules, _

import logging
import time

_logger = logging.getLogger(__name__)


class EmployeeSyncUser(models.Model):
    _inherit = "hr.employee"
    _description = "Enterprise WeChat employees bind system users"

    def sync_as_user(self):
        """[summary]
        运行同步
        """
        start = time.time()
        results = ""
        result = ""
        params = self.env["ir.config_parameter"].sudo()
        debug = params.get_param("wxwork.debug_enabled")
        if debug:
            _logger.info(_("Start batch generating system users from employees"))

        # 获取 标记为 企业微信组织 的公司
        companies = (
            self.sudo()
            .env["res.company"]
            .search([(("is_wxwork_organization", "=", True))])
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
                            ("is_wxwork_employee", "=", True),
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
                                ("wxwork_id", "=", employee.wxwork_id),
                                ("is_wxwork_user", "=", True),
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
        debug = params.get_param("wxwork.debug_enabled")
        groups_id = (
            self.sudo().env["res.groups"].search([("id", "=", 9),], limit=1,).id
        )  # id=9是门户用户
        try:
            user = user.create(
                {
                    "company_ids": [(6, 0, [employee.company_id.id])],
                    "company_id": employee.company_id.id,
                    "name": employee.name,
                    "login": employee.wxwork_id,
                    "password": self.env["wxwork.tools"].random_passwd(8),  # 随机8位密码
                    "email": employee.work_email,
                    "wxwork_id": employee.wxwork_id,
                    "image_1920": employee.image_1920,
                    "qr_code": employee.qr_code,
                    "active": employee.active,
                    "mobile": employee.mobile_phone,
                    "phone": employee.work_phone,
                    "is_wxwork_user": True,
                    "is_moderator": False,
                    "is_company": False,
                    "employee": True,
                    "share": False,
                    "groups_id": [(6, 0, [groups_id])],  # 设置用户为门户用户
                    "tz": "Asia/Chongqing",
                    "lang": "zh_CN",
                }
            )
            if user.id:
                employee.write(
                    {
                        "user_id": user.id,
                        "address_home_id": user.partner_id.id,
                        "user_check_tick": True,
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
        debug = params.get_param("wxwork.debug_enabled")

        user.write(
            {
                "name": employee.name,
                "image_1920": employee.image_1920,
                "is_wxwork_user": True,
                "mobile": employee.mobile_phone,
                "phone": employee.work_phone,
            }
        )


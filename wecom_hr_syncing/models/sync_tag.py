# -*- coding: utf-8 -*-

from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException
from odoo import api, fields, models, _
import logging
import time

_logger = logging.getLogger(__name__)


class SyncTag(models.AbstractModel):
    _name = "wecom.sync_task_tag"
    _description = "Wecom Synchronize tag tasks"

    def run(self, company):
        params = self.env["ir.config_parameter"].sudo()
        debug = params.get_param("wecom.debug_enabled")
        if debug:
            _logger.info(_("Start syncing WeCom Tags of %s") % company.name)

        times = time.time()
        try:
            start1 = time.time()

            wxapi = self.env["wecom.service_api"].init_api(
                company, "contacts_secret", "contacts"
            )
            # status = True
            response = wxapi.httpCall(
                self.env["wecom.service_api_list"].get_server_api_call("TAG_GET_LIST")
            )  # 获取标签列表

            # 同步企业微信标签
            for obj in response["taglist"]:
                self.run_sync(company, obj)
                # sync = self.run_sync(obj)
                # if sync == False:
                #     status = False
            end1 = time.time()
            times1 = end1 - start1

            start2 = time.time()
            # 处理移除无效的员工标签
            tags = (
                self.env["hr.employee.category"]
                .sudo()
                .search(
                    [
                        ("is_wecom_category", "=", True),
                        ("company_id", "=", company.id),
                        ("tagid", "!=", 0),
                    ]
                )
            )
            if not tags:
                pass
            else:
                self.handling_invalid_tags(company, response, tags)  # 处理移除无效企业微信标签
            end2 = time.time()
            times2 = end2 - start2

            # 标签绑定部门和员工
            start3 = time.time()
            self.binding_tag(company, response)
            end3 = time.time()
            times3 = end3 - start3

            times = times1 + times2 + times3
            # status = {"employee_category": True}
            result = _("WeCom tags sync successfully")
        except ApiException as e:
            if debug:
                _logger.warning(
                    _("Contacts tags error synchronizing '%s', error reason: %s")
                    % (
                        company.name,
                        e.errMsg,
                    )
                )
            result = _("Failed to synchronize tags for '%s'" % company.name)
            # status = {"employee_category": False}

        if debug:
            _logger.info(
                _(
                    "End '%s' WeCom Contact - Tags synchronization,Total time spent: %s seconds"
                )
                % (company.name, times)
            )
        # return times, status, result
        return times, result

    @api.model
    def run_sync(self, company, obj):
        tag = (
            self.env["hr.employee.category"]
            .sudo()
            .search(
                [
                    ("tagid", "=", obj["tagid"]),
                    ("company_id", "=", company.id),
                ],
                limit=1,
            )
        )
        try:
            if not tag:
                self.create_tag(company, tag, obj)
            else:
                self.update_tag(company, tag, obj)

        except Exception as e:
            params = self.env["ir.config_parameter"].sudo()
            debug = params.get_param("wecom.debug_enabled")
            if debug:
                _logger.warning(
                    _("WeCom contacts tags synchronization failed, error: %s")
                    % repr(e),
                )
            # return False

    def create_tag(self, company, records, obj):
        try:
            records.create(
                {
                    "name": obj["tagname"],
                    "color": self.env["hr.employee.category"]._get_default_color(),
                    "tagid": obj["tagid"],
                    "company_id": company.id,
                    "is_wecom_category": True,
                }
            )
            # result = True
        except Exception as e:
            params = self.env["ir.config_parameter"].sudo()
            debug = params.get_param("wecom.debug_enabled")
            if debug:
                _logger.warning(_("Error creating tag: %s") % repr(e))
            # result = False
        # return result

    def update_tag(self, company, records, obj):
        try:
            records.write(
                {
                    "name": obj["tagname"],
                }
            )
            result = True
        except Exception as e:
            params = self.env["ir.config_parameter"].sudo()
            debug = params.get_param("wecom.debug_enabled")
            if debug:
                _logger.warning(_("Update tag error: %s") % repr(e))
            result = False

        return result

    def handling_invalid_tags(self, company, wxwork, odoo):
        """比较企业微信和odoo的标签数据"""

        try:
            list_wecom_tags = []
            list_odoo_tags = []

            for wecom_tag in wxwork["taglist"]:
                list_wecom_tags.append(wecom_tag["tagid"])

            for odoo_tag in odoo:
                list_odoo_tags.append(odoo_tag.tagid)

            # 生成odoo与企业微信不同的标签列表
            invalid_tags = list(set(list_odoo_tags).difference(set(list_wecom_tags)))

            # 移除无效的标签
            for invalid_tag in invalid_tags:
                invalid_odoo_tag = (
                    self.env["hr.employee.category"]
                    .sudo()
                    .search(
                        [
                            ("tagid", "=", invalid_tag),
                            ("company_id", "=", company.id),
                        ]
                    )
                )
                if invalid_odoo_tag:
                    invalid_odoo_tag.unlink()
        except Exception as e:
            params = self.env["ir.config_parameter"].sudo()
            debug = params.get_param("wecom.debug_enabled")
            if debug:
                _logger.warning(
                    _("Failed to remove invalid employee tag: %s") % (repr(e))
                )

    @api.model
    def binding_tag(self, company, response):
        """
        HR绑定标签
        """
        params = self.env["ir.config_parameter"].sudo()
        debug = params.get_param("wecom.debug_enabled")
        # 遍历员工标签
        for res in response["taglist"]:
            employee_category = (
                self.env["hr.employee.category"]
                .sudo()
                .search([("tagid", "=", res["tagid"]), ("company_id", "=", company.id)])
            )
            employees = []
            departments = []
            try:
                wxapi = self.env["wecom.service_api"].init_api(
                    company, "contacts_secret", "contacts"
                )
                tags = wxapi.httpCall(
                    self.env["wecom.service_api_list"].get_server_api_call(
                        "TAG_GET_MEMBER"
                    ),
                    {"tagid": str(res["tagid"])},
                )

                userlist = tags["userlist"]  # 标签中包含的员工列表

                if not userlist:
                    pass
                else:
                    for tag_employee in userlist:
                        employee = (
                            self.env["hr.employee"]
                            .sudo()
                            .search(
                                [
                                    ("wecom_user_id", "=", tag_employee["userid"]),
                                    ("company_id", "=", company.id),
                                ]
                            )
                        )
                        employees.append(employee.id)
                    if len(employees) > 0:
                        employee_category.write({"employee_ids": [(6, 0, employees)]})

                partylist = tags["partylist"]  # 标签中包含的部门列表

                if not partylist:
                    pass
                else:
                    for tag_department in partylist:
                        department = (
                            self.env["hr.department"]
                            .sudo()
                            .search(
                                [
                                    ("wecom_department_id", "=", tag_department),
                                    ("company_id", "=", company.id),
                                ]
                            )
                        )
                        departments.append(department.id)
                        if len(departments) > 0:
                            employee_category.write(
                                {"department_ids": [(6, 0, departments)]}
                            )
            except ApiException as e:
                if debug:
                    _logger.warning(_("Set Tag error: %s") % (e.errMsg))

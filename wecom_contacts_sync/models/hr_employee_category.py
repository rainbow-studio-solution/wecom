# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import logging
import time
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException

_logger = logging.getLogger(__name__)


class EmployeeCategory(models.Model):
    _inherit = "hr.employee.category"

    # -------------------------------------------------------
    # 同步标签
    # -------------------------------------------------------
    def sync_tag(self, company):
        res = {}
        start_time = time.time()
        state = None

        params = self.env["ir.config_parameter"].sudo()
        debug = params.get_param("wecom.debug_enabled")
        if debug:
            _logger.info(_("Start syncing WeCom Tags of %s") % company.name)

        try:  
            wxapi = self.env["wecom.service_api"].InitServiceApi(
                company.corpid, company.contacts_app_id.secret
            )
            # status = True
            response = wxapi.httpCall(
                self.env["wecom.service_api_list"].get_server_api_call("TAG_GET_LIST")
            )  # 获取标签列表            
        except ApiException as e:
            state = "fail"
            result = _("Contacts tags error synchronizing '%s', error reason: %s")  % (company.name, e.errMsg)
            if debug:
                _logger.warning(result)
            result = _("Failed to synchronized '%s''s WeCom tags") % company.name
            # status = {"employee_category": False}
        else:
            # 同步企业微信标签
            for obj in response["taglist"]:
                self.run_sync(company, obj)
 
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
  

            # 标签绑定部门和员工
            self.binding_tag(company, response)

            state = "completed"
            result = _("Successfully synchronized '%s''s WeCom tags") % company.name
        finally:
            end_time = time.time()
            if debug:
                _logger.info(
                    _(
                        "End '%s' WeCom Contact - Tags synchronization,Total time spent: %s seconds"
                    )
                    % (company.name, end_time-start_time)
                )
            res.update({
                "tag_sync_times":end_time-start_time,
                "tag_sync_state":state,
                "tag_sync_result":result,
                })
            return res

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
                wxapi = self.env["wecom.service_api"].InitServiceApi(
                    company.corpid, company.contacts_app_id.secret
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
                                    ("wecom_userid", "=", tag_employee["userid"]),
                                    ("company_id", "=", company.id),
                                    "|",
                                    ("active", "=", True),
                                    ("active", "=", False),
                                ]
                            )
                        )

                        if employee:
                            # print("employee------------", employee.id)
                            employees.append(employee.id)
                    # print("employees------------", employees)
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

# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import logging
import time
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException

_logger = logging.getLogger(__name__)


class EmployeeCategory(models.Model):
    _inherit = "hr.employee.category"

    def sync_employee_tags(self):
        params = self.env["ir.config_parameter"].sudo()
        debug = params.get_param("wecom.debug_enabled")

        company = self.company_id
        if not company:
            company = self.env.company

        if debug:
            _logger.info(_("Start syncing WeCom Contact - Employee Tags"))

        times = time.time()
        try:
            start1 = time.time()
            wxapi = self.env["wecom.service_api"].InitServiceApi(
                company.corpid, company.contacts_app_id.secret
            )

            status = True
            response = wxapi.httpCall(
                self.env["wecom.service_api_list"].get_server_api_call("TAG_GET_LIST")
            )

            # 同步企业微信标签
            for obj in response["taglist"]:
                sync = self.run_sync(obj, debug)
                if sync == False:
                    status = False
            end1 = time.time()
            times1 = end1 - start1

            start2 = time.time()
            # 处理移除无效企业微信标签
            tags = self.search([("is_wecom_category", "=", True), ("tagid", "!=", 0)])
            if not tags:
                pass
            else:
                self.handling_invalid_tags(response, tags, debug)  # 处理移除无效企业微信标签
            end2 = time.time()
            times2 = end2 - start2

            # 标签绑定员工
            start3 = time.time()
            self.employee_binding_tag(response, params)
            end3 = time.time()
            times3 = end3 - start3

            times = times1 + times2 + times3
            status = {"employee_category": True}
            result = _("WeCom employee tags sync successfully")
        except ApiException as e:
            if debug:
                _logger.warning(
                    _("Contacts employee tags synchronization error: %s") % (e.errMsg)
                )
            result = _("Failed to synchronize employee tags")
            status = {"employee_category": False}

        if debug:
            _logger.info(
                _("End sync WeCom Contact - Employee Tags,Total time spent: %s seconds")
                % times
            )
        return times, status, result

    @api.model
    def run_sync(self, obj, debug):
        tag = self.search([("tagid", "=", obj["tagid"])], limit=1,)
        try:
            if not tag:
                status = self.create_employee_tag(tag, obj, debug)
            else:
                status = self.update_employee_tag(tag, obj, debug)
            return status
        except Exception as e:
            if debug:
                print(
                    _("WeCom contacts employee tags synchronization failed, error: %s")
                    % repr(e)
                )
            return False

    def create_employee_tag(self, records, obj, debug):
        try:
            records.create(
                {
                    "name": obj["tagname"],
                    "color": self._get_default_color(),
                    "tagid": obj["tagid"],
                    "is_wecom_category": True,
                }
            )
            result = True
        except Exception as e:
            if debug:
                print(_("Error creating employee tag: %s") % (obj["name"], repr(e)))
            result = False
        return result

    def update_employee_tag(self, records, obj, debug):
        try:
            records.write(
                {"name": obj["tagname"],}
            )
            result = True
        except Exception as e:
            if debug:
                print(_("Update employee tag error: %s") % (obj["name"], repr(e)))
            result = False

        return result

    def handling_invalid_tags(self, wxwork, odoo, debug):
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
                invalid_odoo_tag = self.search([[("tagid", "=", invalid_tag)]])
                if invalid_odoo_tag:
                    invalid_odoo_tag.unlink()
        except Exception as e:
            if debug:
                print(_("Failed to remove invalid employee tag: %s") % (repr(e)))

    @api.model
    def employee_binding_tag(self, response, params):
        """
        HR绑定标签
        """
        debug = params.get_param("wecom.debug_enabled")
        corpid = params.get_param("wecom.corpid")
        secret = params.get_param("wecom.contacts_secret")

        for res in response["taglist"]:
            employee_category = self.search([("tagid", "=", res["tagid"]),])
            employees = []
            try:
                wxapi = CorpApi(corpid, secret)
                tags = wxapi.httpCall(
                    CORP_API_TYPE["TAG_GET_USER"], {"tagid": str(res["tagid"]),},
                )
                userlist = tags["userlist"]  # 标签中包含的成员列表

                if not userlist:
                    pass
                else:
                    for tag_employee in userlist:
                        employee = self.env["hr.employee"].search(
                            [("wecom_userid", "=", tag_employee["userid"]),]
                        )
                        employees.append(employee.id)
                    if len(employees) > 0:
                        employee_category.write({"employee_ids": [(6, 0, employees)]})
            except BaseException as e:
                if debug:
                    _logger.info(_("Set employee Tag error: %s") % (repr(e)))

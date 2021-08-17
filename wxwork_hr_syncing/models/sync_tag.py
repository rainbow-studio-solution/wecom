# -*- coding: utf-8 -*-

from odoo.addons.wxwork_api.api.corp_api import CorpApi, CORP_API_TYPE
from odoo import api, fields, models, _
import logging
import time

_logger = logging.getLogger(__name__)


class SyncTag(object):
    def __init__(self, kwargs):
        self.kwargs = kwargs
        self.corpid = self.kwargs["company"].corpid
        self.secret = self.kwargs["company"].contacts_secret
        self.debug = self.kwargs["debug"]
        self.company = self.kwargs["company"]
        self.department = self.kwargs["department"]
        self.employee = self.kwargs["employee"]
        self.employee_category = self.kwargs["employee_category"]

    def run(self):

        if self.debug:
            _logger.info(
                _("Start syncing Enterprise WeChat Tags of %s") % self.company.name
            )

        times = time.time()
        try:
            start1 = time.time()

            wxapi = CorpApi(self.corpid, self.secret)
            # status = True
            response = wxapi.httpCall(CORP_API_TYPE["TAG_GET_LIST"])  # 获取标签列表

            # 同步企业微信标签
            for obj in response["taglist"]:
                self.run_sync(obj)
                # sync = self.run_sync(obj)
                # if sync == False:
                #     status = False
            end1 = time.time()
            times1 = end1 - start1

            start2 = time.time()
            # 处理移除无效的员工标签
            tags = self.employee_category.sudo().search(
                [
                    ("is_wxwork_category", "=", True),
                    ("company_id", "=", self.company.id),
                    ("tagid", "!=", 0),
                ]
            )
            if not tags:
                pass
            else:
                self.handling_invalid_tags(response, tags)  # 处理移除无效企业微信标签
            end2 = time.time()
            times2 = end2 - start2

            # 标签绑定部门和员工
            start3 = time.time()
            self.binding_tag(response)
            end3 = time.time()
            times3 = end3 - start3

            times = times1 + times2 + times3
            # status = {"employee_category": True}
            result = _("Enterprise WeChat tags sync successfully")
        except BaseException as e:
            if self.debug:
                _logger.info(_("Contacts tags synchronization error: %s") % (repr(e)))
            result = _("Failed to synchronize tags")
            # status = {"employee_category": False}

        if self.debug:
            _logger.info(
                _(
                    "End sync Enterprise WeChat Contact - Tags,Total time spent: %s seconds"
                )
                % times
            )
        # return times, status, result
        return times, result

    @api.model
    def run_sync(self, obj):
        tag = self.employee_category.sudo().search(
            [("tagid", "=", obj["tagid"]), ("company_id", "=", self.company.id),],
            limit=1,
        )
        try:
            if not tag:
                self.create_tag(tag, obj)
            else:
                self.update_tag(tag, obj)

        except Exception as e:
            if self.debug:
                print(
                    _(
                        "Enterprise WeChat contacts tags synchronization failed, error: %s"
                    )
                    % repr(e),
                )
            # return False

    def create_tag(self, records, obj):
        try:
            records.create(
                {
                    "name": obj["tagname"],
                    "color": self.employee_category._get_default_color(),
                    "tagid": obj["tagid"],
                    "company_id": self.company.id,
                    "is_wxwork_category": True,
                }
            )
            # result = True
        except Exception as e:
            if self.debug:
                print(_("Error creating tag: %s") % repr(e))
            # result = False
        # return result

    def update_tag(self, records, obj):
        try:
            records.write(
                {"name": obj["tagname"],}
            )
            result = True
        except Exception as e:
            if self.debug:
                print(_("Update tag error: %s") % repr(e))
            result = False

        return result

    def handling_invalid_tags(self, wxwork, odoo):
        """比较企业微信和odoo的标签数据"""

        try:
            list_wxwork_tags = []
            list_odoo_tags = []

            for wxwork_tag in wxwork["taglist"]:
                list_wxwork_tags.append(wxwork_tag["tagid"])

            for odoo_tag in odoo:
                list_odoo_tags.append(odoo_tag.tagid)

            # 生成odoo与企业微信不同的标签列表
            invalid_tags = list(set(list_odoo_tags).difference(set(list_wxwork_tags)))

            # 移除无效的标签
            for invalid_tag in invalid_tags:
                invalid_odoo_tag = self.employee_category.sudo().search(
                    [("tagid", "=", invalid_tag), ("company_id", "=", self.company.id),]
                )
                if invalid_odoo_tag:
                    invalid_odoo_tag.unlink()
        except Exception as e:
            if self.debug:
                print(_("Failed to remove invalid employee tag: %s") % (repr(e)))

    @api.model
    def binding_tag(self, response):
        """
        HR绑定标签
        """
        # 遍历员工标签
        for res in response["taglist"]:
            employee_category = self.employee_category.sudo().search(
                [("tagid", "=", res["tagid"]), ("company_id", "=", self.company.id)]
            )
            employees = []
            departments = []
            try:
                wxapi = CorpApi(self.corpid, self.secret)
                tags = wxapi.httpCall(
                    CORP_API_TYPE["TAG_GET_MEMBER"], {"tagid": str(res["tagid"])},
                )
                userlist = tags["userlist"]  # 标签中包含的员工列表

                if not userlist:
                    pass
                else:
                    for tag_employee in userlist:
                        employee = self.employee.sudo().search(
                            [
                                ("wxwork_id", "=", tag_employee["userid"]),
                                ("company_id", "=", self.company.id),
                            ]
                        )
                        employees.append(employee.id)
                    if len(employees) > 0:
                        employee_category.write({"employee_ids": [(6, 0, employees)]})

                partylist = tags["partylist"]  # 标签中包含的部门列表

                if not partylist:
                    pass
                else:
                    for tag_department in partylist:
                        department = self.department.sudo().search(
                            [
                                ("wxwork_department_id", "=", tag_department),
                                ("company_id", "=", self.company.id),
                            ]
                        )
                        departments.append(department.id)
                        if len(departments) > 0:
                            employee_category.write(
                                {"department_ids": [(6, 0, departments)]}
                            )
            except BaseException as e:
                if self.debug:
                    _logger.info(_("Set Tag error: %s") % (repr(e)))

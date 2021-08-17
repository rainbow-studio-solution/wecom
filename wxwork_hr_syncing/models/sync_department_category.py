# -*- coding: utf-8 -*-

from odoo.addons.wxwork_api.api.corp_api import CorpApi, CORP_API_TYPE
from odoo import api, fields, models, _
import logging
import time

_logger = logging.getLogger(__name__)


class SyncDepartmentCategory(object):
    def __init__(self, kwargs):
        self.kwargs = kwargs
        self.corpid = self.kwargs["company"].corpid
        self.secret = self.kwargs["company"].contacts_secret
        self.debug = self.kwargs["debug"]
        self.company = self.kwargs["company"]
        self.department_id = self.kwargs["company"].contacts_sync_hr_department_id
        self.department = self.kwargs["department"]
        self.department_category = self.kwargs["department_category"]

    @api.model
    def run(self):
        if self.debug:
            _logger.info(
                _("Start synchronizing the enterprise wechat Department tags of %s"),
                self.company.name,
            )
        wxapi = CorpApi(self.corpid, self.secret)

        result = ""
        times = 0
        try:
            start1 = time.time()

            # 获取标签列表
            response = wxapi.httpCall(CORP_API_TYPE["TAG_GET_LIST"])

            # 同步企业微信部门标签
            for tag in response["taglist"]:
                self.run_sync(tag, wxapi)
            end1 = time.time()
            times1 = end1 - start1

            # 处理移除无效企业微信标签
            start2 = time.time()
            tags = self.department_category.sudo().search(
                [
                    ("is_wxwork_category", "=", True),
                    ("company_id", "=", self.company.id),
                    ("tagid", "!=", 0),
                ]
            )

            # if not tags:
            #     pass
            # else:
            #     self.handling_invalid_tags(response, tags)  # 处理移除无效企业微信标签
            end2 = time.time()
            times2 = end2 - start2

            # 标签绑定部门
            start3 = time.time()
            # self.department_binding_tag(response)
            end3 = time.time()
            times3 = end3 - start3
            times = times1 + times2 + times3
            # status = {"department_category": True}
            result = _("Enterprise WeChat department tags sync successfully")
            result = (
                _("Department tags of %s were synchronized successfully")
                % self.company.name
            )
        except BaseException as e:
            if self.debug:
                _logger.warning(
                    _(
                        "The tag of enterprise wechat Department of %s is wrong. Details: %s"
                    ),
                    self.company.name,
                    repr(e),
                )
            result = (
                _("Failed to synchronize the enterprise wechat Department tag of %s."),
                self.company.name,
            )

        # return times, status, result
        return times, result

    def run_sync(self, wxtag, wxapi):
        """[summary]

        Args:
            wxtag ([type]): [description]企业微信标签
            wxapi ([type]): [description]企业微信API对象
        """
        # 获取标签成员
        response = wxapi.httpCall(
            CORP_API_TYPE["TAG_GET_MEMBER"], {"tagid": str(wxtag["tagid"])}
        )
        departments = response["partylist"]
        if len(departments) > 0:
            # for department in departments:
            tag = self.department_category.sudo().search(
                [("tagid", "=", wxtag["tagid"]), ("company_id", "=", self.company.id),],
                limit=1,
            )
            if not tag:
                self.create_department_tag(tag, wxtag)
            else:
                self.update_department_tag(tag, wxtag)

    def create_department_tag(self, records, wxtag):
        records.create(
            {
                "name": wxtag["tagname"],
                "company_id": self.company.id,
                "color": self.department_category._get_default_color(),
                "tagid": wxtag["tagid"],
                "is_wxwork_category": True,
            }
        )

    def update_department_tag(self, records, wxtag):
        records.write(
            {"name": wxtag["tagname"],}
        )

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
                invalid_odoo_tag = self.department_category.sudo().search(
                    [
                        [
                            ("tagid", "=", invalid_tag),
                            ("company_id", "=", self.company.id),
                        ]
                    ]
                )
                if invalid_odoo_tag:
                    invalid_odoo_tag.unlink()
        except Exception as e:
            if self.debug:
                print(_("Failed to remove invalid department tag: %s") % (repr(e)))

    def department_binding_tag(self, response):
        """
        HR部门绑定标签
        """

        for res in response["taglist"]:
            department_category = self.department_category.sudo().search(
                [("tagid", "=", res["tagid"]), ("company_id", "=", self.company.id)]
            )
            departments = []
            try:
                wxapi = CorpApi(self.corpid, self.secret)
                tags = wxapi.httpCall(
                    CORP_API_TYPE["TAG_GET_USER"], {"tagid": str(res["tagid"]),},
                )

                partylist = tags["partylist"]  # 标签中包含的部门id列表

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
                        department_category.write(
                            {"department_ids": [(6, 0, departments)]}
                        )
            except BaseException as e:
                if self.debug:
                    _logger.info(
                        _(
                            "Error setting enterprise wechat Department Tag of %s,error details:  %s"
                        )
                        % (self.company.name, repr(e))
                    )

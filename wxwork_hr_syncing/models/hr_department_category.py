# -*- coding: utf-8 -*-

from odoo.addons.wxwork_api.api.corp_api import CorpApi, CORP_API_TYPE
from odoo import api, fields, models, _
import logging
import time

_logger = logging.getLogger(__name__)


class DepartmentCategory(models.Model):
    _inherit = "hr.department.category"

    def sync_department_tags(self, company):
        pass
        # params = self.env["ir.config_parameter"].sudo()
        # debug = params.get_param("wxwork.debug_enabled")
        # corpid = params.get_param("wxwork.corpid")
        # secret = params.get_param("wxwork.contacts_secret")
        # if debug:
        #     _logger.info(_("Start syncing Enterprise WeChat Contact - Department Tags"))

        # times = time.time()
        # try:
        #     start1 = time.time()

        #     wxapi = CorpApi(corpid, secret)
        #     status = True
        #     response = wxapi.httpCall(CORP_API_TYPE["TAG_GET_LIST"])
        #     # 同步企业微信标签
        #     for obj in response["taglist"]:
        #         sync = self.run_sync(obj, debug)
        #         if sync == False:
        #             status = False
        #     end1 = time.time()
        #     times1 = end1 - start1

        #     start2 = time.time()
        #     # 处理移除无效企业微信标签
        #     tags = self.search([("is_wxwork_category", "=", True), ("tagid", "!=", 0)])
        #     if not tags:
        #         pass
        #     else:
        #         self.handling_invalid_tags(response, tags, debug)  # 处理移除无效企业微信标签
        #     end2 = time.time()
        #     times2 = end2 - start2

        #     # 标签绑定员工
        #     start3 = time.time()
        #     self.department_binding_tag(response, params)
        #     end3 = time.time()
        #     times3 = end3 - start3

        #     times = times1 + times2 + times3
        #     status = {"department_category": True}
        #     result = _("Enterprise WeChat department tags sync successfully")
        # except BaseException as e:
        #     if debug:
        #         _logger.info(
        #             _("Contacts department tags synchronization error: %s") % (repr(e))
        #         )
        #     result = _("Failed to synchronize department tags")
        #     status = {"department_category": False}

        # if debug:
        #     _logger.info(
        #         _(
        #             "End sync Enterprise WeChat Contact - Department Tags,Total time spent: %s seconds"
        #         )
        #         % times
        #     )
        # return times, status, result

    @api.model
    def run_sync(self, obj, debug):
        tag = self.search([("tagid", "=", obj["tagid"])], limit=1,)
        try:
            if not tag:
                status = self.create_department_tag(tag, obj, debug)
            else:
                status = self.update_department_tag(tag, obj, debug)
            return status
        except Exception as e:
            if debug:
                print(
                    _(
                        "Enterprise WeChat contacts department tags synchronization failed, error: %s"
                    )
                    % repr(e)
                )
            return False

    def create_department_tag(self, records, obj, debug):
        try:
            records.create(
                {
                    "name": obj["tagname"],
                    "color": self._get_default_color(),
                    "tagid": obj["tagid"],
                    "is_wxwork_category": True,
                }
            )
            result = True
        except Exception as e:
            if debug:
                print(_("Error creating department tag: %s") % (obj["name"], repr(e)))
            result = False
        return result

    def update_department_tag(self, records, obj, debug):
        try:
            records.write(
                {"name": obj["tagname"],}
            )
            result = True
        except Exception as e:
            if debug:
                print(_("Update department tag error: %s") % (obj["name"], repr(e)))
            result = False

        return result

    def handling_invalid_tags(self, wxwork, odoo, debug):
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
                invalid_odoo_tag = self.search([[("tagid", "=", invalid_tag)]])
                if invalid_odoo_tag:
                    invalid_odoo_tag.unlink()
        except Exception as e:
            if debug:
                print(_("Failed to remove invalid department tag: %s") % (repr(e)))

    def department_binding_tag(self, response, params):
        """
        HR绑定标签
        """
        debug = params.get_param("wxwork.debug_enabled")
        corpid = params.get_param("wxwork.corpid")
        secret = params.get_param("wxwork.contacts_secret")

        for res in response["taglist"]:
            department_category = self.env["hr.department.category"].search(
                [("tagid", "=", res["tagid"]),]
            )
            departments = []
            try:
                wxapi = CorpApi(corpid, secret)
                tags = wxapi.httpCall(
                    CORP_API_TYPE["TAG_GET_USER"], {"tagid": str(res["tagid"]),},
                )

                partylist = tags["partylist"]  # 标签中包含的部门id列表

                if not partylist:
                    pass
                else:
                    for tag_department in partylist:
                        department = self.env["hr.department"].search(
                            [("wxwork_department_id", "=", tag_department),]
                        )
                        departments.append(department.id)
                    if len(departments) > 0:
                        department_category.write(
                            {"department_ids": [(6, 0, departments)]}
                        )
            except BaseException as e:
                if debug:
                    _logger.info(_("Set department Tag error: %s") % (repr(e)))

# -*- coding: utf-8 -*-

from ...wxwork_api.wx_qy_api.CorpApi import CORP_API_TYPE, CorpApi
from odoo import api, fields, models, _
import logging
import time

_logger = logging.getLogger(__name__)


class EmployeeCategory(models.Model):
    _inherit = "hr.employee.category"

    def sync_wxwork_contacts_tags(self):
        params = self.env["ir.config_parameter"].sudo()
        debug = params.get_param("wxwork.debug_enabled")
        corpid = params.get_param("wxwork.corpid")
        secret = params.get_param("wxwork.contacts_secret")
        if debug:
            _logger.info(_("Start synchronizing contacts tags from Enterprise WeChat"))

        times = time.time()
        try:
            start = time.time()

            wxapi = CorpApi(corpid, secret)
            response = wxapi.httpCall(CORP_API_TYPE["TAG_GET_LIST"])
            # 同步企业微信标签
            for obj in response["taglist"]:
                self.run_sync(obj, debug)

            tags = self.search([("is_wxwork_category", "=", True)])
            # TODO 待处理移除无效企业微信标签

            end = time.time()
            times = end - start
            status = True
            result = _("Enterprise WeChat tags sync successfully")
            print(response)
        except BaseException as e:
            if debug:
                _logger.info(_("Contacts tags synchronization  error: %s") % (repr(e)))
            result = _("Failed to synchronize contacts tags")
            status = False
        return times, status, result

    def run_sync(self, obj, debug):
        tag = self.search([("tagid", "=", obj["tagid"])], limit=1,)
        try:
            if not tag:
                self.create_tag(tag, obj, debug)
            else:
                self.update_tag(tag, obj, debug)
        except Exception as e:
            if debug:
                print(
                    _(
                        "Enterprise WeChat contacts tags synchronization failed, error: %s"
                    )
                    % repr(e)
                )

    def create_employee(self, records, obj, debug):
        try:
            records.create(
                {
                    "name": obj["name"],
                    "tagid": obj["tagid"],
                    "is_wxwork_category": True,
                }
            )
            result = True
        except Exception as e:
            if debug:
                print(_("Error creating tag: %s") % (obj["name"], repr(e)))
            result = False
        return result

    def update_tag(self, records, obj, debug):
        try:
            records.write(
                {"name": obj["name"],}
            )
            result = True
        except Exception as e:
            if debug:
                print(_("Update tag error: %s") % (obj["name"], repr(e)))
            result = False

        return result


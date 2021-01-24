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
            status = True
            response = wxapi.httpCall(CORP_API_TYPE["TAG_GET_LIST"])
            # 同步企业微信标签
            for obj in response["taglist"]:
                sync = self.run_sync(obj, debug)
                if sync == False:
                    status = False

            # 处理移除无效企业微信标签
            tags = self.search([("is_wxwork_category", "=", True), ("tagid", "!=", 0)])
            if not tags:
                pass
            else:
                self.handling_invalid_tags(response, tags, debug)  # 处理移除无效企业微信标签

            end = time.time()
            times = end - start
            status = True
            result = _("Enterprise WeChat tags sync successfully")
        except BaseException as e:
            if debug:
                _logger.info(_("Contacts tags synchronization  error: %s") % (repr(e)))
            result = _("Failed to synchronize contacts tags")
            status = False
        return times, status, result

    @api.model
    def run_sync(self, obj, debug):
        tag = self.search([("tagid", "=", obj["tagid"])], limit=1,)
        try:
            if not tag:
                status = self.create_tag(tag, obj, debug)
            else:
                status = self.update_tag(tag, obj, debug)
            return status
        except Exception as e:
            if debug:
                print(
                    _(
                        "Enterprise WeChat contacts tags synchronization failed, error: %s"
                    )
                    % repr(e)
                )
            return False

    def create_tag(self, records, obj, debug):
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
                print(_("Error creating tag: %s") % (obj["name"], repr(e)))
            result = False
        return result

    def update_tag(self, records, obj, debug):
        try:
            records.write(
                {"name": obj["tagname"],}
            )
            result = True
        except Exception as e:
            if debug:
                print(_("Update tag error: %s") % (obj["name"], repr(e)))
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
                print(_("Failed to remove invalid tag: %s") % (repr(e)))

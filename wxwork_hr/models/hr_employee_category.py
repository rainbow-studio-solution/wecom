# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import logging
import time
from ...wxwork_api.wx_qy_api.CorpApi import CORP_API_TYPE, CorpApi
from ...wxwork_api.wx_qy_api.AbstractApi import ApiException
from ...wxwork_api.wx_qy_api.ErrorCode import *

_logger = logging.getLogger(__name__)


class EmployeeCategory(models.Model):
    _inherit = "hr.employee.category"

    tagid = fields.Integer(
        string="Enterprise WeChat Tag ID",
        readonly=True,
        default=0,
        help="标签id，非负整型，指定此参数时新增的标签会生成对应的标签id，不指定时则以目前最大的id自增。",
    )
    is_wxwork_category = fields.Boolean(string="Enterprise WeChat Tag", default=False,)

    def update_to_wxwork(self):
        params = self.env["ir.config_parameter"].sudo()
        debug = params.get_param("wxwork.debug_enabled")
        corpid = params.get_param("wxwork.corpid")
        secret = params.get_param("wxwork.contacts_secret")

        wxapi = CorpApi(corpid, secret)
        params = {}
        try:
            if self.tagid:
                if debug:
                    _logger.info(
                        _("Update contacts tags: %s to Enterprise WeChat") % self.name
                    )
                response = wxapi.httpCall(
                    CORP_API_TYPE["TAG_UPDATE"],
                    {"tagid": self.tagid, "tagname": self.name},
                )
                message = _("Successfully updated tag.")
            else:
                if debug:
                    _logger.info(
                        _("Create contacts tags: %s to Enterprise WeChat") % self.name
                    )
                response = wxapi.httpCall(
                    CORP_API_TYPE["TAG_CREATE"], {"tagname": self.name}
                )
                self.write({"tagid": response["tagid"]})
                message = _("Tag successfully created.")

            if response["errcode"] == 0:
                params = {
                    "title": _("Success"),
                    "message": message,
                    "sticky": False,  # 延时关闭
                    "className": "bg-success",
                    "next": {"type": "ir.actions.client", "tag": "reload",},  # 刷新窗体
                }
                action = {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": params["title"],
                        "type": "success",
                        "message": params["message"],
                        "sticky": params["sticky"],
                        "next": params["next"],
                    },
                }
                return action
        except ApiException as ex:
            params = {
                "title": _("Failed"),
                "message": _(
                    "Error code: %s "
                    + "\n"
                    + "Error description: %s"
                    + "\n"
                    + "Error Details:"
                    + "\n"
                    + "%s"
                )
                % (str(ex.errCode), Errcode.getErrcode(ex.errCode), ex.errMsg),
                "sticky": True,  # 不会延时关闭，需要手动关闭
                "next": {},
            }
            action = {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    # "className": "wxwork_config_notification",
                    "title": params["title"],
                    "type": "danger",
                    "message": params["message"],
                    "sticky": params["sticky"],  # 不会延时关闭，需要手动关闭
                    "next": params["next"],
                },
            }
            return action

    def delete_to_wxwork(self):
        params = self.env["ir.config_parameter"].sudo()
        debug = params.get_param("wxwork.debug_enabled")
        corpid = params.get_param("wxwork.corpid")
        secret = params.get_param("wxwork.contacts_secret")

        if debug:
            _logger.info(_("Delete contacts tags: %s to Enterprise WeChat") % self.name)

        wxapi = CorpApi(corpid, secret)
        params = {}
        try:
            response = wxapi.httpCall(
                CORP_API_TYPE["TAG_DELETE"], {"tagid": str(self.tagid)}
            )
            if response["errcode"] == 0:
                params = {
                    "title": _("Success"),
                    "type": "success",
                    "message": _("Tag: %s deleted successfully.") % self.name,
                    "sticky": False,  # 延时关闭
                    "className": "bg-success",
                    "next": {"type": "ir.actions.client", "tag": "reload",},  # 刷新窗体
                }
                tag = self.search([("tagid", "=", self.tagid)], limit=1,)
                tag.unlink()
            else:
                params = {
                    "title": _("SuFailedccess"),
                    "type": "danger",
                    "message": _("Tag: %s deletion failed.") % self.name,
                    "sticky": False,  # 延时关闭
                    "className": "bg-success",
                    "next": {"type": "ir.actions.client", "tag": "reload",},  # 刷新窗体
                }
            action = {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": params["title"],
                    "type": params["type"],
                    "message": params["message"],
                    "sticky": params["sticky"],
                    "next": params["next"],
                },
            }

            return action
        except ApiException as ex:
            params = {
                "title": _("Failed"),
                "message": _(
                    "Error code: %s "
                    + "\n"
                    + "Error description: %s"
                    + "\n"
                    + "Error Details:"
                    + "\n"
                    + "%s"
                )
                % (str(ex.errCode), Errcode.getErrcode(ex.errCode), ex.errMsg),
                "sticky": True,  # 不会延时关闭，需要手动关闭
                "next": {},
            }
            action = {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    # "className": "wxwork_config_notification",
                    "title": params["title"],
                    "type": "danger",
                    "message": params["message"],
                    "sticky": params["sticky"],  # 不会延时关闭，需要手动关闭
                    "next": params["next"],
                },
            }
            return action

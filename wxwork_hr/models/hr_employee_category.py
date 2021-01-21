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
        help="标签id，非负整型，指定此参数时新增的标签会生成对应的标签id，不指定时则以目前最大的id自增。",
    )
    is_wxwork_category = fields.Boolean(string="Enterprise WeChat Tag", default=False,)

    def update_to_wxwork(self):
        params = self.env["ir.config_parameter"].sudo()
        debug = params.get_param("wxwork.debug_enabled")
        corpid = params.get_param("wxwork.corpid")
        secret = params.get_param("wxwork.contacts_secret")
        if debug:
            _logger.info(
                _("Synchronizing contacts tags: %s to Enterprise WeChat") % self.name
            )
            wxapi = CorpApi(corpid, secret)
            params = {}
            try:
                response = wxapi.httpCall(
                    CORP_API_TYPE["TAG_CREATE"], {"tagname": self.name}
                )
                if response["errcode"] == 0:
                    self.write({"tagid": response["tagid"]})
                    params = {
                        "title": _("Success"),
                        "message": _("Successfully updated tag."),
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

    # @api.model
    # def create(self, vals):
    #     """
    #     创建标签时，判断是否时企业微信联系人的标签
    #     """
    #     if vals["is_wxwork_category"]:
    #         pass

    #     tag = super(EmployeeCategory, self).create(vals)
    #     return tag

# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import logging
import time
from odoo.exceptions import UserError

from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException

_logger = logging.getLogger(__name__)


class EmployeeCategory(models.Model):
    _inherit = "hr.employee.category"

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        index=True,
        default=lambda self: self.env.company,
        readonly=True,
    )
    department_ids = fields.Many2many(
        "hr.department",
        "department_category_rel",
        "category_id",
        "dmp_id",
        string="Departments",
    )
    tagid = fields.Integer(
        string="WeCom Tag ID",
        readonly=True,
        default=0,
        help="Tag ID, non negative integer. When this parameter is specified, the new tag will generate the corresponding tag ID. if it is not specified, it will be automatically increased by the current maximum ID.",
    )
    is_wecom_category = fields.Boolean(
        string="WeCom Tag",
        default=False,
    )

    def update_to_wxwork(self):
        debug = self.env["ir.config_parameter"].sudo().get_param("wecom.debug_enabled")
        company = self.company_id

        params = {}
        try:
            wxapi = self.env["wecom.service_api"].init_api(
                company, "contacts_secret", "contacts"
            )
            if self.tagid:
                if debug:
                    _logger.info(_("Update contacts tags: %s to WeCom") % self.name)
                response = wxapi.httpCall(
                    self.env["wecom.service_api_list"].get_server_api_call(
                        "TAG_UPDATE"
                    ),
                    {"tagid": self.tagid, "tagname": self.name},
                )

                message = _("Successfully updated tag.")
            else:
                if debug:
                    _logger.info(_("Create contacts tags: %s to WeCom") % self.name)
                response = wxapi.httpCall(
                    self.env["wecom.service_api_list"].get_server_api_call(
                        "TAG_CREATE"
                    ),
                    {"tagname": self.name},
                )

                self.write({"tagid": response["tagid"]})
                message = _("Tag successfully created.")

            if response["errcode"] == 0:
                params = {
                    "title": _("Success"),
                    "message": message,
                    "sticky": False,  # 延时关闭
                    "className": "bg-success",
                    "next": {
                        "type": "ir.actions.client",
                        "tag": "reload",
                    },  # 刷新窗体
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
            return self.env["wecom.tools"].ApiExceptionDialog(ex)

    def delete_to_wxwork(self):
        debug = self.env["ir.config_parameter"].sudo().get_param("wecom.debug_enabled")
        company = self.company_id

        if debug:
            _logger.info(_("Delete contacts tags: %s to WeCom") % self.name)

        params = {}
        try:
            wxapi = self.env["wecom.service_api"].init_api(
                company, "contacts_secret", "contacts"
            )
            response = wxapi.httpCall(
                self.env["wecom.service_api_list"].get_server_api_call("TAG_DELETE"),
                {"tagid": str(self.tagid)},
            )

            if response["errcode"] == 0:
                params = {
                    "title": _("Success"),
                    "type": "success",
                    "message": _("Tag: %s deleted successfully.") % self.name,
                    "sticky": False,  # 延时关闭
                    "className": "bg-success",
                    "next": {
                        "type": "ir.actions.client",
                        "tag": "reload",
                    },  # 刷新窗体
                }
                tag = self.search(
                    [("tagid", "=", self.tagid)],
                    limit=1,
                )
                tag.unlink()
            else:
                params = {
                    "title": _("Failed"),
                    "type": "danger",
                    "message": _("Tag: %s deletion failed.") % self.name,
                    "sticky": False,  # 延时关闭
                    "className": "bg-success",
                    "next": {
                        "type": "ir.actions.client",
                        "tag": "reload",
                    },  # 刷新窗体
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
            return self.env["wecom.tools"].ApiExceptionDialog(ex)

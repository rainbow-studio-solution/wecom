# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import logging
import time
import json
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
    display_name = fields.Char(string="Display Name", compute="_compute_display_name")
    employee_ids = fields.Many2many(
        "hr.employee",
        "employee_category_rel",
        "category_id",
        "emp_id",
        string="Employees",
    )
    department_ids = fields.Many2many(
        "hr.department",
        "department_category_rel",
        "category_id",
        "dmp_id",
        string="Departments",
    )
    is_change = fields.Boolean(string="Is Change", default=False)
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

    @api.depends("is_wecom_category")
    def _compute_display_name(self):
        tag = _("WeCom")
        for rec in self:
            if rec.is_wecom_category:
                rec.display_name = "%s:%s" % (tag, rec.name)
            else:
                rec.display_name = rec.name

    def write(self, vals):
        """
        保存时，同步当前记录到企业微信
        """
        res = super(EmployeeCategory, self).write(vals)
        # if "employee_ids" in vals or "department_ids" in vals:
        #     print(vals.get("employee_ids")[0][2])
        #     print(vals.get("department_ids")[0][2])
        return res

    # ------------------------------------------------------------
    # 企微标签
    # ------------------------------------------------------------
    def create_wecom_tag(self):
        """
        创建企微标签
        """
        debug = self.env["ir.config_parameter"].sudo().get_param("wecom.debug_enabled")
        company = self.company_id
        if not company:
            company = self.env.company

        params = {}
        try:
            wxapi = self.env["wecom.service_api"].InitServiceApi(
                company.corpid, company.contacts_app_id.secret
            )
            if self.tagid:
                if debug:
                    _logger.info(_("Update contacts tags: %s to WeCom") % self.name)
                response = wxapi.httpCall(
                    self.env["wecom.service_api_list"].get_server_api_call(
                        "TAG_CREATE"
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
            return self.env["wecomapi.tools.action"].ApiExceptionDialog(
                ex, raise_exception=True
            )

    def update_wecom_tag_name(self):
        debug = self.env["ir.config_parameter"].sudo().get_param("wecom.debug_enabled")
        company = self.company_id
        if not company:
            company = self.env.company

        params = {}
        try:
            wxapi = self.env["wecom.service_api"].InitServiceApi(
                company.corpid, company.contacts_app_id.secret
            )
            if self.tagid:
                if debug:
                    _logger.info(
                        _("Update contacts tags: %s name to WeCom") % self.name
                    )
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
                        # "next": params["next"],
                    },
                }
                return action
        except ApiException as ex:
            return self.env["wecomapi.tools.action"].ApiExceptionDialog(
                ex, raise_exception=True
            )

    def delete_wecom_tag(self):
        """
        删除企微标签
        """
        debug = self.env["ir.config_parameter"].sudo().get_param("wecom.debug_enabled")
        company = self.company_id
        if not company:
            company = self.env.company

        if debug:
            _logger.info(_("Delete contacts tags: %s to WeCom") % self.name)

        params = {}
        try:
            wxapi = self.env["wecom.service_api"].InitServiceApi(
                company.corpid, company.contacts_app_id.secret
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
                tag.write(
                    {
                        "is_wecom_category": False,
                        "tagid": 0,
                    }
                )
                # tag.unlink()
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
            return self.env["wecomapi.tools.action"].ApiExceptionDialog(
                ex, raise_exception=True
            )

    # ------------------------------------------------------------
    # 企微标签成员
    # ------------------------------------------------------------
    def sync_tag_members(self):
        """
        标签成员数据比较
        """
        # TODO 待添加弹框提醒

        debug = self.env["ir.config_parameter"].sudo().get_param("wecom.debug_enabled")
        company = self.company_id
        if not company:
            company = self.env.company
        params = {}
        try:
            wxapi = self.env["wecom.service_api"].InitServiceApi(
                company.corpid, company.contacts_app_id.secret
            )
            if self.tagid:
                if debug:
                    _logger.info(
                        _("Delete contacts tag [%s] member to WeCom") % self.name
                    )
                # 企业微信上的标签成员数据列表
                get_response = wxapi.httpCall(
                    self.env["wecom.service_api_list"].get_server_api_call(
                        "TAG_GET_MEMBER"
                    ),
                    {"tagid": str(self.tagid)},
                )
                remote_userlist = []
                remote_partylist = []
                if get_response["errcode"] == 0:
                    for user in get_response["userlist"]:
                        remote_userlist.append(user["userid"])

                    for party in get_response["partylist"]:
                        remote_partylist.append(party)

                # 本地数据列表
                local_userlist = []
                if self.employee_ids:
                    for user in self.employee_ids:
                        local_userlist.append(user.wecom_userid)

                local_partylist = []
                if self.department_ids:
                    for department in self.department_ids:
                        local_partylist.append(department.wecom_department_id)

                # 交集
                intersection_userlist = list(
                    set(remote_userlist).intersection(set(local_userlist))
                )
                intersection_partylist = list(
                    set(remote_partylist).intersection(set(local_partylist))
                )

                # 需要上传到企业微信差集
                upload_userlist = list(
                    set(local_userlist).difference(set(remote_userlist))
                )
                upload_partylist = list(
                    set(local_partylist).difference(set(remote_partylist))
                )

                # 需要下载到本地差集
                download_userlist = list(
                    set(remote_userlist).difference(set(local_userlist))
                )
                download_partylist = list(
                    set(remote_partylist).difference(set(local_partylist))
                )
                # print(download_userlist, download_partylist)
                # print(upload_userlist, upload_partylist)
                # 下载差集
                self.tag_member_download(download_userlist, download_partylist)
                # 上传差集
                self.tag_member_upload(wxapi, upload_userlist, upload_partylist)

        except ApiException as ex:
            return self.env["wecomapi.tools.action"].ApiExceptionDialog(
                ex, raise_exception=True
            )

    def tag_member_download(self, userlist, partylist):
        """
        下载企微标签数据到本地
        """
        company = self.company_id
        if not company:
            company = self.env.company

        for user in userlist:
            employee = (
                self.env["hr.employee"]
                .sudo()
                .search(
                    [
                        ("wecom_userid", "=", user),
                        ("company_id", "=", company.id),
                        ("is_wecom_employee", "=", True),
                        "|",
                        ("active", "=", True),
                        ("active", "=", False),
                    ],
                    limit=1,
                )
            )
            if employee not in self.employee_ids:
                # department_list.append(department.id)
                self.write({"employee_ids": [(4, employee.id)]})
        #     employees.append(employee.id)
        #     if employee not in self.employee_ids:
        #         print("----------", employee)
        #         # employee_list.append(employee.id)
        # print("----------", employees)
        # self.write({"employee_ids": [(6, 0, employees)]})

        for party in partylist:
            department = (
                self.env["hr.department"]
                .sudo()
                .search(
                    [
                        ("wecom_department_id", "=", party),
                        ("is_wecom_department", "=", True),
                        ("company_id", "=", company.id),
                        "|",
                        ("active", "=", True),
                        ("active", "=", False),
                    ],
                )
            )
            if department not in self.department_ids:
                # department_list.append(department.id)
                self.write({"department_ids": [(4, department.id)]})

    def tag_member_upload(self, wxapi, userlist, partylist):
        """
        上传本地标签数据到企微
        """
        # print("-----上传", userlist, partylist)
        if len(userlist) > 0 or len(partylist) > 0:
            response = wxapi.httpCall(
                self.env["wecom.service_api_list"].get_server_api_call(
                    "TAG_ADD_MEMBER"
                ),
                {
                    "tagid": str(self.tagid),
                    "userlist": userlist,
                    "partylist": partylist,
                },
            )

    def remove_user_from_tag(self):
        print("tag--Remove from tag")

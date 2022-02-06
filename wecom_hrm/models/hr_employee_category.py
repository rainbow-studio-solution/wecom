# -*- coding: utf-8 -*-

import logging
import base64
from lxml import etree
from odoo import api, fields, models, _
from lxml_to_dict import lxml_to_dict
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException
_logger = logging.getLogger(__name__)

WECOM_USER_MAPPING_ODOO_EMPLOYEE_CATEGORY = {
    "TagId": "tagid",  # 标签Id
    "AddUserItems": "add_employee_ids",  # 标签中新增的成员userid列表，用逗号分隔
    "DelUserItems": "del_employee_ids",  # 标签中删除的成员userid列表，用逗号分隔
    "AddPartyItems": "add_department_ids",  # 标签中新增的部门id列表，用逗号分隔
    "DelPartyItems": "del_department_ids",  # 标签中删除的部门id列表，用逗号分隔
}


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

    tagid = fields.Integer(
        string="WeCom Tag ID",
        readonly=True,
        default=0,
        help="Tag ID, non negative integer. When this parameter is specified, the new tag will generate the corresponding tag ID. if it is not specified, it will be automatically increased by the current maximum ID.",
    )
    is_wecom_category = fields.Boolean(string="WeCom Tag", default=False,)

    @api.depends("is_wecom_category")
    def _compute_display_name(self):
        tag = _("WeCom")
        for rec in self:
            if rec.is_wecom_category:
                rec.display_name = "%s:%s" % (tag, rec.name)
            else:
                rec.display_name = rec.name

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
                    "next": {"type": "ir.actions.client", "tag": "reload",},  # 刷新窗体
                }
                tag = self.search([("tagid", "=", self.tagid)], limit=1,)
                tag.write(
                    {"is_wecom_category": False, "tagid": 0,}
                )
                # tag.unlink()
            else:
                params = {
                    "title": _("Failed"),
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
                        ("is_wecom_user", "=", True),
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

    def remove_obj_from_tag(self, tagid=False, model="", res_id=False):
        tag = self.browse(tagid)
        tag_member_name = self.env["ir.model"]._get(model).model

        userlist = []
        partylist = []
        ids_name = ""
        tag_member_model_obj = self.env[tag_member_name].browse(res_id)
        if tag_member_name == "hr.employee":
            userlist.append(tag_member_model_obj.wecom_userid)
            ids_name = "employee_ids"
        elif tag_member_name == "hr.department":
            partylist.append(tag_member_model_obj.wecom_department_id)
            ids_name = "department_ids"

        try:
            wxapi = self.env["wecom.service_api"].InitServiceApi(
                tag.company_id.corpid, tag.company_id.contacts_app_id.secret
            )
            response = wxapi.httpCall(
                self.env["wecom.service_api_list"].get_server_api_call(
                    "TAG_DELETE_MEMBER"
                ),
                {"tagid": str(tagid), "userlist": userlist, "partylist": partylist,},
            )
            if response["errcode"] == 0:
                # 删除成功
                # print("API删除成功")
                tag.write({ids_name: [(3, res_id)]})
                return True
            else:
                return False

        except ApiException as ex:
            error = self.env["wecom.service_api_error"].get_error_by_code(ex.errCode)
            _logger.warning(
                _("Wecom API error: %s, error name: %s, error message: %s")
                % (str(ex.errCode), error["name"], ex.errMsg)
            )
            return False


    def wecom_event_change_contact_tag(self, cmd):
        """
        通讯录事件更新标签
        """
        xml_tree = self.env.context.get("xml_tree")
        company_id = self.env.context.get("company_id")
        xml_tree_str = etree.fromstring(bytes.decode(xml_tree))
        dic = lxml_to_dict(xml_tree_str)["xml"]
        # print("tag dic", dic)

        callback_tag = (
            self.env["hr.employee.category"]
            .sudo()
            .search(
                [("company_id", "=", company_id.id), ("tagid", "=", dic["TagId"])],
                limit=1,
            )
        )
        domain = [
            "|",
            ("active", "=", True),
            ("active", "=", False),
        ]
        employee = (
            self.env["hr.employee"]
            .sudo()
            .search([("company_id", "=", company_id.id)] + domain)
        )
        department = (
            self.env["hr.department"]
            .sudo()
            .search([("company_id", "=", company_id.id)] + domain)
        )

        update_dict = {}

        for key, value in dic.items():
            if (
                key == "ToUserName"
                or key == "FromUserName"
                or key == "CreateTime"
                or key == "Event"
                or key == "MsgType"
                or key == "ChangeType"
            ):
                # 忽略掉 不需要的key
                pass
            else:
                if key in WECOM_USER_MAPPING_ODOO_EMPLOYEE_CATEGORY.keys():
                    if WECOM_USER_MAPPING_ODOO_EMPLOYEE_CATEGORY[key] != "":
                        update_dict[
                            WECOM_USER_MAPPING_ODOO_EMPLOYEE_CATEGORY[key]
                        ] = value
                    else:
                        _logger.info(
                            _(
                                "There is no mapping for field [%s], please contact the developer."
                            )
                            % key
                        )
        # print("update_dict", update_dict)
        add_employee_list = []
        del_employee_list = []
        add_department_list = []
        del_department_list = []

        if "add_employee_ids" in update_dict.keys():
            for wecom_userid in update_dict["add_employee_ids"].split(","):
                add_employee_list.append(
                    employee.search([("wecom_userid", "=", wecom_userid)], limit=1).id
                )
        elif "del_employee_ids" in update_dict.keys():
            for wecom_userid in update_dict["del_employee_ids"].split(","):
                del_employee_list.append(
                    employee.search([("wecom_userid", "=", wecom_userid)], limit=1).id
                )
        elif "add_department_ids" in update_dict.keys():
            for wecom_department_id in update_dict["add_department_ids"].split(","):
                add_department_list.append(
                    department.search(
                        [("wecom_department_id", "=", wecom_department_id)], limit=1,
                    ).id
                )
        elif "del_department_ids" in update_dict.keys():
            for wecom_department_id in update_dict["del_department_ids"].split(","):
                del_department_list.append(
                    department.search(
                        [("wecom_department_id", "=", wecom_department_id)], limit=1,
                    ).id
                )

        # print(
        #     add_employee_list,
        #     del_employee_list,
        #     add_department_list,
        #     del_department_list,
        # )
        if len(add_employee_list) > 0:
            callback_tag.write(
                {"employee_ids": [(4, res, False) for res in add_employee_list]}
            )
        if len(del_employee_list) > 0:
            callback_tag.write(
                {"employee_ids": [(3, res, False) for res in del_employee_list]}
            )
        if len(add_department_list) > 0:
            callback_tag.write(
                {"department_ids": [(4, res, False) for res in add_department_list]}
            )
        if len(del_department_list) > 0:
            callback_tag.write(
                {"department_ids": [(3, res, False) for res in del_department_list]}
            )

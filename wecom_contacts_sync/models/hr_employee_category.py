# -*- coding: utf-8 -*-

import logging
import base64
import time
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
        domain="[('company_id', '=', company_id)]",
    )
    department_ids = fields.Many2many(
        "hr.department",
        "department_category_rel",
        "category_id",
        "dmp_id",
        string="Departments",
        domain="[('company_id', '=', company_id)]",
    )

    tagid = fields.Integer(
        string="WeCom Tag ID",
        readonly=True,
        default=0,
        help="Tag ID, non negative integer. When this parameter is specified, the new tag will generate the corresponding tag ID. if it is not specified, it will be automatically increased by the current maximum ID.",
    )
    is_wecom_tag = fields.Boolean(string="WeCom Tag", default=False,)

    @api.depends("is_wecom_tag")
    def _compute_display_name(self):
        tag = _("WeCom Tag")
        for rec in self:
            if rec.is_wecom_tag:
                rec.display_name = "%s:%s" % (tag, rec.name)
            else:
                rec.display_name = rec.name

    @api.onchange("employee_ids")
    def _onchange_employee_ids(self):
        if self.is_wecom_tag:
            self.change = True

    @api.onchange("department_ids")
    def _onchange_department_ids(self):
        if self.is_wecom_tag:
            self.change = True

    def unlink(self):
        del_wecom_tag = (
            self.env["ir.config_parameter"].sudo().get_param("wecom.del_wecom_tag")
        )
        for tag in self:
            if tag.is_wecom_tag and del_wecom_tag:
                tag.delete_wecom_tag()
        return super(EmployeeCategory, self).unlink()

    # ------------------------------------------------------------
    # 企微标签及企微标签成员
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

    def upload_wecom_tag(self):
        """
        上传企微标签
        """
        debug = self.env["ir.config_parameter"].sudo().get_param("wecom.debug_enabled")
        params = {}
        try:
            wxapi = self.env["wecom.service_api"].InitServiceApi(
                self.company_id.corpid, self.company_id.contacts_app_id.secret
            )
            tagid = 0
            # 创建标签和更新标签
            if self.tagid:
                tagid = self.tagid
                # 更新标签
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
                # 创建标签
                if debug:
                    _logger.info(_("Create contacts tags: %s to WeCom") % self.name)
                if debug:
                    _logger.info(_("Create contacts tags: %s to WeCom") % self.name)
                response = wxapi.httpCall(
                    self.env["wecom.service_api_list"].get_server_api_call(
                        "TAG_CREATE"
                    ),
                    {"tagname": self.name},
                )
                tagid = response["tagid"]
                message = _("Tag successfully created.")

            if tagid:
                # 比较本地和远程数据，增加和删除标签成员
                add_tag_members, del_tag_members = self.upload_compare_data(
                    wxapi, tagid
                )

                add_tag_members.update({"tagid": tagid})
                del_tag_members.update({"tagid": tagid})

                if (
                    len(add_tag_members["userlist"]) > 0
                    or len(add_tag_members["partylist"]) > 0
                ):
                    # 添加远程标签成员
                    response = wxapi.httpCall(
                        self.env["wecom.service_api_list"].get_server_api_call(
                            "TAG_ADD_MEMBER"
                        ),
                        add_tag_members,
                    )
                if (
                    len(del_tag_members["userlist"]) > 0
                    or len(del_tag_members["partylist"]) > 0
                ):
                    # 删除远程标签尘缘
                    response = wxapi.httpCall(
                        self.env["wecom.service_api_list"].get_server_api_call(
                            "TAG_DELETE_MEMBER"
                        ),
                        del_tag_members,
                    )
        except ApiException as ex:
            error = self.env["wecom.service_api_error"].get_error_by_code(ex.errCode)
            params.update(
                {
                    "title": _("Fail"),
                    "message": _("API error: %s, error name: %s, error message: %s")
                    % (str(ex.errCode), error["name"], ex.errMsg),
                    "type": "warning",
                    "sticky": True,
                    "className": "bg-warning",
                }
            )
        else:
            params.update(
                {
                    "title": _("Success"),
                    "message": message,
                    "type": "success",
                    "sticky": False,  # 延时关闭
                    "className": "bg-success",
                }
            )
            print(tagid)
            if response["errmsg"] == "created":
                self.write({"tagid": tagid})
                params.update(
                    {"next": {"type": "ir.actions.client", "tag": "reload",},}  # 刷新窗体
                )

        finally:
            action = {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": params,
            }
            return action

    def upload_compare_data(self, wxapi, tagid):
        """
        上传:比较本地和远程数据
        """
        # 企业微信上的标签成员数据列表
        response = wxapi.httpCall(
            self.env["wecom.service_api_list"].get_server_api_call("TAG_GET_MEMBER"),
            {"tagid": str(tagid)},
        )
        remote_userlist = []
        remote_partylist = []
        if response["errcode"] == 0:
            for user in response["userlist"]:
                remote_userlist.append(user["userid"].lower())

            for party in response["partylist"]:
                remote_partylist.append(party)

        # 本地数据列表
        local_userlist = []
        local_partylist = []
        if self.employee_ids:
            for user in self.employee_ids:
                local_userlist.append(user.wecom_userid)

        if self.department_ids:
            for department in self.department_ids:
                local_partylist.append(department.wecom_department_id)

        # 本地与远程的差集，及需要在远程增加的数据
        remote_add_userlist = list(set(local_userlist).difference(set(remote_userlist)))
        remote_add_partylist = list(
            set(local_partylist).difference(set(remote_partylist))
        )
        add_tag_members = {
            "userlist": [user for user in remote_add_userlist],
            "partylist": [party for party in remote_add_partylist],
        }

        # 远程与本地的差集，及需要在远程删除的数据
        remote_del_userlist = list(set(remote_userlist).difference(set(local_userlist)))
        remote_del_partylist = list(
            set(remote_partylist).difference(set(local_partylist))
        )
        del_tag_members = {
            "userlist": [user for user in remote_del_userlist],
            "partylist": [party for party in remote_del_partylist],
        }

        return add_tag_members, del_tag_members

    def download_wecom_tag(self):
        """
        下载单个企微标签
        """
        debug = self.env["ir.config_parameter"].sudo().get_param("wecom.debug_enabled")
        params = {}
        try:
            wxapi = self.env["wecom.service_api"].InitServiceApi(
                self.company_id.corpid, self.company_id.contacts_app_id.secret
            )

            tag_response = wxapi.httpCall(
                self.env["wecom.service_api_list"].get_server_api_call("TAG_GET_LIST")
            )
        except ApiException as ex:
            error = self.env["wecom.service_api_error"].get_error_by_code(ex.errCode)
            params.update(
                {
                    "title": _("Fail"),
                    "message": _("API error: %s, error name: %s, error message: %s")
                    % (str(ex.errCode), error["name"], ex.errMsg),
                    "type": "warning",
                    "sticky": True,
                    "className": "bg-warning",
                }
            )
        else:
            tags = tag_response["taglist"]

            for tag in tags:
                if tag["tagid"] == self.tagid:
                    self.name = tag["tagname"]
                    result = self.download_wecom_tag_member(
                        self, wxapi, tag["tagid"], self.company_id
                    )
                    if result is False:
                        params.update(
                            {
                                "title": _("Fail"),
                                "message": _("Tag downloaded failed."),
                                "type": "warning",
                                "sticky": True,
                                "className": "bg-warning",
                            }
                        )
                        action = {
                            "type": "ir.actions.client",
                            "tag": "display_notification",
                            "params": params,
                        }
                        return action

            message = _("Tag downloaded successfully.")
            params.update(
                {
                    "title": _("Success"),
                    "message": message,
                    "type": "success",
                    "sticky": True,  # 延时关闭
                    "className": "bg-success",
                    "next": {"type": "ir.actions.client", "tag": "reload",},
                }
            )
        finally:
            action = {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": params,
            }
            return action

    @api.model
    def download_wecom_tags(self):
        """
        下载企微标签列表 hr.employee.category
        """
        start_time = time.time()
        company = self.env.context.get("company_id")

        tasks = []
        if not company:
            company = self.env.company
        if company.is_wecom_organization:
            try:
                wxapi = self.env["wecom.service_api"].InitServiceApi(
                    company.corpid, company.contacts_app_id.secret
                )
                response = wxapi.httpCall(
                    self.env["wecom.service_api_list"].get_server_api_call(
                        "TAG_GET_LIST"
                    )
                )

            except ApiException as ex:
                end_time = time.time()
                self.env["wecomapi.tools.action"].ApiExceptionDialog(
                    ex, raise_exception=False
                )
                tasks = [
                    {
                        "name": "download_tag_data",
                        "state": False,
                        "time": end_time - start_time,
                        "msg": str(ex),
                    }
                ]
            except Exception as e:
                end_time = time.time()
                tasks = [
                    {
                        "name": "download_tag_data",
                        "state": False,
                        "time": end_time - start_time,
                        "msg": str(e),
                    }
                ]
            else:
                tags = response["taglist"]
                for tag in tags:
                    category = self.search(
                        [
                            ("tagid", "=", tag["tagid"]),
                            ("company_id", "=", company.id),
                        ],
                        limit=1,
                    )

                    if not category:
                        category.create(
                            {
                                "name": tag["tagname"],
                                "tagid": tag["tagid"],
                                "is_wecom_tag": True,
                            }
                        )
                    else:
                        category.write(
                            {"name": tag["tagname"], "is_wecom_tag": True,}
                        )
                    result = self.download_wecom_tag_member(
                        category, wxapi, tag["tagid"], company
                    )
                    if result:
                        tasks.append(
                            {
                                "name": "download_tag_members",
                                "state": False,
                                "time": 0,
                                "msg": _(
                                    "Failed to download tag [%s] member of company [%s]!"
                                )
                                % (tag["tagname"], company.name),
                            }
                        )
            finally:
                end_time = time.time()
                task = {
                    "name": "download_tag_data",
                    "state": True,
                    "time": end_time - start_time,
                    "msg": _("Tag list downloaded successfully."),
                }
                tasks.append(task)
        else:
            end_time = time.time()
            tasks = [
                {
                    "name": "download_tag_data",
                    "state": False,
                    "time": end_time - start_time,
                    "msg": _(
                        "The current company does not identify the enterprise wechat organization. Please configure or switch the company."
                    ),
                }
            ]
        return tasks

    def download_wecom_tag_member(self, category, wxapi, tagid, company):
        """
        下载企微标签成员
        """
        res = {}
        try:
            response = wxapi.httpCall(
                self.env["wecom.service_api_list"].get_server_api_call(
                    "TAG_GET_MEMBER"
                ),
                {"tagid": str(tagid)},
            )
        except ApiException as ex:
            self.env["wecomapi.tools.action"].ApiExceptionDialog(
                ex, raise_exception=False
            )
            res = {
                "name": "download_tag_members",
                "state": False,
                "time": 0,
                "msg": repr(e),
            }
        except Exception as e:
            res = {
                "name": "download_tag_members",
                "state": False,
                "time": 0,
                "msg": repr(e),
            }
        else:
            employee_ids = []
            for user in response["userlist"]:
                employee = (
                    self.env["hr.employee"]
                    .sudo()
                    .search(
                        [
                            ("wecom_userid", "=", user["userid"].lower()),
                            ("company_id", "=", company.id),
                            ("is_wecom_user", "=", True),
                            "|",
                            ("active", "=", True),
                            ("active", "=", False),
                        ],
                        limit=1,
                    )
                )
                if employee:
                    employee_ids.append(employee.id)
            if len(employee_ids) > 0:
                category.write({"employee_ids": [(6, 0, employee_ids)]})

            department_ids = []
            for party in response["partylist"]:
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
                if department:
                    department_ids.append(department.id)
            if len(department_ids) > 0:
                category.write({"department_ids": [(6, 0, department_ids)]})
        finally:
            return res  # 返回失败的结果

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
                    {"is_wecom_tag": False, "tagid": 0,}
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
    # 企微通讯录事件
    # ------------------------------------------------------------
    def wecom_event_change_contact_tag(self, cmd):
        """
        通讯录事件更新标签
        """
        xml_tree = self.env.context.get("xml_tree")
        company_id = self.env.context.get("company_id")
        xml_tree_str = etree.fromstring(bytes.decode(xml_tree))
        dic = lxml_to_dict(xml_tree_str)["xml"]

        callback_tag = self.sudo().search(
            [("company_id", "=", company_id.id), ("tagid", "=", dic["TagId"])], limit=1,
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
                    employee.search(
                        [("wecom_userid", "=", wecom_userid.lower())], limit=1
                    ).id
                )
        elif "del_employee_ids" in update_dict.keys():
            for wecom_userid in update_dict["del_employee_ids"].split(","):
                del_employee_list.append(
                    employee.search(
                        [("wecom_userid", "=", wecom_userid.lower())], limit=1
                    ).id
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

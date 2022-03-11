# -*- coding: utf-8 -*-


from odoo import _, api, fields, models
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException

import json


class WeComUser(models.Model):
    _name = "wecom.users"
    _description = "Wecom User"

    company_id = fields.Many2one("res.company", "Company")

    name = fields.Char(
        string="Name",
        copy=False,
    )
    english_name = fields.Char(
        string="English Name",
        copy=False,
    )
    wecom_userid = fields.Char(
        string="User ID",
        copy=False,
    )
    department = fields.Char(string="Department", default=[], copy=False)
    # department_ids = fields.One2many(
    #     "wecom.department", "department_id", string="Departments", copy=False
    # )
    main_department = fields.Integer(string="Main Department Id", copy=False)
    main_department_id = fields.Many2one(
        "wecom.department", string="Main Department", copy=False
    )
    order = fields.Char(string="Order value", default=[])
    position = fields.Char(string="Position", copy=False)
    external_position = fields.Char(string="External position", copy=False)
    mobile = fields.Char(string="Mobile", copy=False)
    gender = fields.Selection(
        [("0", "Undefined"), ("1", "Male"), ("2", "Female")],
        string="Gender",
        default="0",
    )
    email = fields.Char(string="Email", copy=False)
    biz_mail = fields.Char(string="Enterprise mailbox", copy=False)
    is_leader_in_dept = fields.Char(string="Department head", default=[])
    direct_leader = fields.Char(string="Direct leader", default=[])
    # direct_leader_ids = fields.One2many(
    #     "wecom.users", "user_id", string="Direct Leaders", copy=False
    # )
    avatar = fields.Char(string="Avatar", copy=False)
    thumb_avatar = fields.Char(string="Avatar Thumbnail", copy=False)
    telephone = fields.Char(string="Telephone", copy=False)
    alias = fields.Char(string="Alias", copy=False)
    address = fields.Char(string="Address", copy=False)
    open_userid = fields.Char(string="Open user id", copy=False)
    extattr = fields.Text(
        string="Extended attributes", copy=False, default={}, force_save=True
    )
    external_profile = fields.Text(
        string="External attributes", copy=False, default={}, force_save=True
    )
    status = fields.Selection(
        [
            ("1", "Activated"),
            ("2", "Disabled"),
            ("4", "Inactive"),
            ("5", "Exited Enterprise"),
        ],
        string="Status",
        default="2",
    )
    qr_code = fields.Char(string="QR code", copy=False)

    @api.model
    def organizational_download(self):
        """
        下载组织架构
        :return:
        """
        companies = (
            self.sudo()
            .env["res.company"]
            .search([(("is_wecom_organization", "=", True))])
        )
        if not companies:
            return False

        for company in companies:
            wxapi = self.env["wecom.service_api"].InitServiceApi(
                company.corpid, company.contacts_app_id.secret
            )
            department_response = wxapi.httpCall(
                self.env["wecom.service_api_list"].get_server_api_call(
                    "DEPARTMENT_LIST"
                )
            )

            departments = department_response["department"]
            for wecom_department in departments:
                department = (
                    self.env["wecom.department"]
                    .sudo()
                    .search(
                        [
                            ("department_id", "=", wecom_department["id"]),
                            ("company_id", "=", company.id),
                        ],
                        limit=1,
                    )
                )
                self.create_or_update_department(company, department, wecom_department)
            self.set_parent_department(company, departments)

            user_response = wxapi.httpCall(
                self.env["wecom.service_api_list"].get_server_api_call("USER_LIST"),
                {
                    "department_id": "1",
                    "fetch_child": "1",
                },
            )
            users = user_response["userlist"]
            for wecom_user in users:
                # print(wecom_user)
                user = (
                    self.env["wecom.users"]
                    .sudo()
                    .search(
                        [
                            ("wecom_userid", "=", wecom_user["userid"].lower()),
                            ("company_id", "=", company.id),
                        ],
                        limit=1,
                    )
                )
                self.create_or_update_user(company, user, wecom_user)
            self.set_main_department(company, users)

    # ------------------------------------------------------------
    # 企微部门
    # ------------------------------------------------------------

    def create_or_update_department(self, company, department, wecom_department):
        """
        创建或更新企微部门
        """
        if not department:
            department.create(
                {
                    "name": wecom_department["name"],
                    "name_en": wecom_department["name_en"]
                    if "name_en" in wecom_department
                    else "",
                    "department_id": wecom_department["id"],
                    "department_leader": wecom_department["department_leader"],
                    "order": wecom_department["order"],
                    "company_id": company.id,
                }
            )
        else:
            department.write(
                {
                    "name": wecom_department["name"],
                    "name_en": wecom_department["name_en"]
                    if "name_en" in wecom_department
                    else "",
                    "department_leader": wecom_department["department_leader"],
                    "order": wecom_department["order"],
                }
            )

    def set_parent_department(self, company, wecom_departments):
        """
        设置上级部门
        """
        for wecom_department in wecom_departments:
            department = (
                self.env["wecom.department"]
                .sudo()
                .search(
                    [
                        ("company_id", "=", company.id),
                        ("department_id", "=", wecom_department["id"]),
                    ],
                    limit=1,
                )
            )
            parent_department = (
                self.env["wecom.department"]
                .sudo()
                .search(
                    [
                        ("company_id", "=", company.id),
                        ("department_id", "=", wecom_department["parentid"]),
                    ],
                    limit=1,
                )
            )
            department.write({"parent_id": parent_department.id})

    # ------------------------------------------------------------
    # 企微用户
    # ------------------------------------------------------------
    def create_or_update_user(self, company, user, wecom_user):
        """
        创建或更新企微用户
        """
        if not user:
            user.create(
                {
                    "name": wecom_user["name"],
                    "english_name": wecom_user["english_name"]
                    if "english_name" in wecom_user
                    else "",
                    "wecom_userid": wecom_user["userid"].lower(),
                    "mobile": wecom_user["mobile"],
                    "email": wecom_user["email"],
                    "department": wecom_user["department"],
                    "main_department": wecom_user["main_department"],
                    "order": str(wecom_user["order"]),
                    "position": wecom_user["position"],
                    "external_position": wecom_user["external_position"]
                    if "external_position" in wecom_user
                    else "",
                    "mobile": wecom_user["mobile"],
                    "gender": wecom_user["gender"],
                    "email": wecom_user["email"],
                    "biz_mail": wecom_user["biz_mail"]
                    if "biz_mail" in wecom_user
                    else "",
                    "is_leader_in_dept": str(wecom_user["is_leader_in_dept"]),
                    "direct_leader": wecom_user["direct_leader"],
                    "avatar": wecom_user["avatar"],
                    "thumb_avatar": wecom_user["thumb_avatar"],
                    "telephone": wecom_user["telephone"],
                    "alias": wecom_user["alias"],
                    "address": wecom_user["address"] if "address" in wecom_user else "",
                    "open_userid": wecom_user["open_userid"]
                    if "open_userid" in wecom_user
                    else "",
                    "extattr": json.dumps(wecom_user["extattr"]),
                    "external_profile": json.dumps(wecom_user["external_profile"])
                    if "external_profile" in wecom_user
                    else "{}",
                    "status": str(wecom_user["status"]),
                    "qr_code": wecom_user["qr_code"],
                    "company_id": company.id,
                }
            )
        else:
            user.write(
                {
                    "name": wecom_user["name"],
                    "english_name": wecom_user["english_name"]
                    if "english_name" in wecom_user
                    else "",
                    "mobile": wecom_user["mobile"],
                    "email": wecom_user["email"],
                    "department": wecom_user["department"],
                    "main_department": wecom_user["main_department"],
                    "order": str(wecom_user["order"]),
                    "position": wecom_user["position"],
                    "external_position": wecom_user["external_position"]
                    if "external_position" in wecom_user
                    else "",
                    "mobile": wecom_user["mobile"],
                    "mobile": wecom_user["mobile"],
                    "gender": wecom_user["gender"],
                    "email": wecom_user["email"],
                    "biz_mail": wecom_user["biz_mail"]
                    if "biz_mail" in wecom_user
                    else "",
                    "is_leader_in_dept": str(wecom_user["is_leader_in_dept"]),
                    "direct_leader": wecom_user["direct_leader"],
                    "avatar": wecom_user["avatar"],
                    "thumb_avatar": wecom_user["thumb_avatar"],
                    "telephone": wecom_user["telephone"],
                    "alias": wecom_user["alias"],
                    "address": wecom_user["address"] if "address" in wecom_user else "",
                    "open_userid": wecom_user["open_userid"]
                    if "open_userid" in wecom_user
                    else "",
                    "extattr": json.dumps(wecom_user["extattr"]),
                    "external_profile": json.dumps(wecom_user["external_profile"])
                    if "external_profile" in wecom_user
                    else "{}",
                    "status": str(wecom_user["status"]),
                    "qr_code": wecom_user["qr_code"],
                }
            )

    def set_main_department(self, company, wecom_userss):
        """
        设置主部门
        """
        for wecom_users in wecom_userss:
            main_department = (
                self.env["wecom.department"]
                .sudo()
                .search(
                    [
                        ("company_id", "=", company.id),
                        ("department_id", "=", wecom_users["main_department"]),
                    ],
                    limit=1,
                )
            )
            user = self.search(
                [
                    ("company_id", "=", company.id),
                    ("wecom_userid", "=", wecom_users["userid"].lower()),
                ],
                limit=1,
            )
            user.sudo().write({"main_department_id": main_department.id})

    # ------------------------------------------------------------
    # 企微标签
    # ------------------------------------------------------------
    def create_or_update_tag(self, user):
        """
        创建或更新企微标签
        """

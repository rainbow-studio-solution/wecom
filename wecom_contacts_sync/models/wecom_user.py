# -*- coding: utf-8 -*-

from asyncio.windows_events import NULL
import logging
import json
from collections import defaultdict
import time
from odoo import fields, models, api, Command, tools, _
from odoo.exceptions import UserError
import xmltodict
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException
from odoo.addons.base.models.ir_mail_server import MailDeliveryException

_logger = logging.getLogger(__name__)


class WecomUser(models.Model):
    _name = "wecom.user"
    _description = "Wecom user"
    _order = "order_in_department"

    # 企微字段
    userid = fields.Char(
        string="User ID",
        readonly=True,
        default="",
    )  # 成员UserID。对应管理端的帐号
    name = fields.Char(string="Name", readonly=True, default="",compute="_compute_name")  # 成员名称
    english_name = fields.Char(
        string="English name", readonly=True, default=""
    )  # 英部门文名称
    mobile = fields.Char(string="mobile phone", readonly=True,default="")  # 手机号码
    department = fields.Char(
        string="Multiple Department ID", readonly=True, store=True, default="[]"
    )  # 成员所属部门id列表

    main_department = fields.Char(
        string="Main department", readonly=True, default=""
    )  # 主部门
    order = fields.Char(
        string="Sequence", readonly=True, default="[]"
    )  # 部门内的排序值，默认为0。数量必须和department一致，数值越大排序越前面。值范围是[0, 2^32)
    position = fields.Char(string="Position", readonly=True, default="")  # 职务信息；
    gender = fields.Char(
        string="Gender", readonly=True, default=""
    )  # 性别。0表示未定义，1表示男性，2表示女性。
    email = fields.Char(string="Email", readonly=True, default="")  # 邮箱
    biz_mail = fields.Char(string="BizMail", readonly=True, default="")  # 企业邮箱
    is_leader_in_dept = fields.Char(
        string="Is Department Leader", readonly=True, default="[]"
    )  # 表示在所在的部门内是否为部门负责人。0-否；1-是。是一个列表，数量必须与department一致。
    direct_leader = fields.Char(
        string="Direct Leader", readonly=True, default="[]"
    )  # 直属上级UserID，返回在应用可见范围内的直属上级列表，最多有五个直属上级
    avatar = fields.Char(string="Avatar", readonly=True, default="")  # 头像url
    thumb_avatar = fields.Char(
        string="Avatar thumbnail", readonly=True, default=""
    )  # 头像缩略图url
    telephone = fields.Char(string="Telephone", readonly=True, default="")  # 座机号码
    alias = fields.Char(string="Alias", readonly=True, default="")  # 别名
    extattr = fields.Text(
        string="Extended attributes", readonly=True, default=""
    )  # 扩展属性
    external_profile = fields.Text(
        string="External attributes", readonly=True, default=""
    )  # 成员对外属性
    external_position = fields.Char(
        string="External position", readonly=True, default=""
    )  # 对外职务，如果设置了该值，则以此作为对外展示的职务，否则以position来展示。
    status = fields.Integer(
        string="Status", readonly=True, default=""
    )  # 激活状态: 1=已激活，2=已禁用，4=未激活，5=退出企业。已激活代表已激活企业微信或已关注微信插件（原企业号）。未激活代表既未激活企业微信又未关注微信插件（原企业号）。
    qr_code = fields.Char(
        string="Personal QR code", readonly=True, default=""
    )  # 员工个人二维码，扫描可添加为外部联系人
    address = fields.Char(string="Address", readonly=True, default="")  # 地址
    open_userid = fields.Char(
        string="Open userid", readonly=True, default=None
    )  # 开放用户Id,全局唯一,对于同一个服务商，不同应用获取到企业内同一个成员的open_userid是相同的，最多64个字节。仅第三方应用可获取

    # odoo 字段
    company_id = fields.Many2one(
        "res.company",
        required=True,
        domain="[('is_wecom_organization', '=', True)]",
        copy=False,
        store=True,
        readonly=True,
    )
    department_id = fields.Many2one(
        "wecom.department",
        "Department",
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        compute="_compute_department_id",
        store=True,
    )
    department_ids = fields.Many2many(
        "wecom.department",
        "wecom_user_department_rel",
        "user_id",
        "department_id",
        string="Multiple Departments",
        readonly=True,
        compute="_compute_department_ids",
    )
    tag_ids = fields.Many2many(
        "wecom.tag",
        "wecom_user_tag_rel",
        "wecom_user_id",
        "wecom_tag_id",
        string="Tags",
    )
    department_complete_name = fields.Char(
        string="Department complete Name", related="department_id.complete_name"
    )
    order_in_department = fields.Integer(
        string="Sequence in department",
        readonly=True,
        default="0",
    )  # 成员在对应部门中的排序值，默认为0。数量必须和department一致
    status_name = fields.Selection(
        [
            ("1", _("Activated")),
            ("2", _("Disabled")),
            ("4", _("Not active")),
            ("5", _("Exit the enterprise")),
        ],
        string="Status",
        readonly=True,
        # compute="_compute_status_name",
    )  # 激活状态: 1=已激活，2=已禁用，4=未激活，5=退出企业。已激活代表已激活企业微信或已关注微信插件（原企业号）。未激活代表既未激活企业微信又未关注微信插件（原企业号）。

    gender_name = fields.Selection(
        [("1", _("Male")), ("2", _("Female")), ("0", _("Undefined"))],
        string="Gender",
        # compute="_compute_gender_name",
    )
    color = fields.Integer("Color Index")
    active = fields.Boolean(
        "Active",
        default=True,
        store=True,
        readonly=True,
        # compute="_compute_active",
    )

    @api.depends("userid")
    def _compute_name(self):
        for user in self:
            if not user.name:
                user.name = user.userid

    @api.depends("status")
    def _compute_status_name(self):
        for user in self:
            user.status_name = str(user.status)

    @api.depends("status")
    def _compute_active(self):
        for user in self:
            if user.status == 1:
                user.active = True
            else:
                user.active = False

    @api.depends("main_department")
    def _compute_department_id(self):
        for user in self:
            department_id = self.env["wecom.department"].search(
                [
                    ("department_id", "=", user.main_department),
                    ("company_id", "=", user.company_id.id),
                ],
                limit=1,
            )
            if department_id:
                user.department_id = department_id

    @api.depends("gender")
    def _compute_gender_name(self):
        for user in self:
            user.gender_name = str(user.gender)

    @api.depends("department")
    def _compute_department_ids(self):
        """
        计算多部门  eval( )
        """
        for user in self:
            department_list = eval(user.department)
            department_ids = self.get_parent_department(
                user.company_id, department_list
            )

            user.write({"department_ids": [(6, 0, department_ids)]})

    def get_parent_department(self, company, departments):
        """
        获取上级部门
        """
        department_ids = []
        for department in departments:
            department_id = self.env["wecom.department"].search(
                [
                    ("department_id", "=", department),
                    ("company_id", "=", company.id),
                ],
                limit=1,
            )
            if department_id:
                department_ids.append(department_id.id)
        return department_ids

    # ------------------------------------------------------------
    # 企微用户下载
    # ------------------------------------------------------------
    @api.model
    def download_wecom_users(self):
        """
        下载用户列表
        """
        start_time = time.time()

        company = self.env.context.get("company_id")
        if type(company) == int:
            company = self.env["res.company"].browse(company)

        tasks = []

        try:
            wxapi = self.env["wecom.service_api"].InitServiceApi(
                company.corpid, company.contacts_app_id.secret
            )

            # 2020-8-27 按照官方API要求，进行重构
            # json对象只有 userid 和 department 两个字段
            # 参数："cursor", 必须:否, 说明:用于分页查询的游标，字符串类型，由上一次调用返回，首次调用不填
            # 参数："limit", 必须:否, 说明:分页，预期请求的数据量，取值范围 1 ~ 10000

            response = wxapi.httpCall(
                self.env["wecom.service_api_list"].get_server_api_call("USER_LIST_ID"),
                {}
                # {"department_id": "1", "fetch_child": "1",},
            )
            
        except ApiException as ex:
            end_time = time.time()

            self.env["wecomapi.tools.action"].ApiExceptionDialog(
                str(ex), raise_exception=False
            )
            tasks = [
                {
                    "name": "download_user_data",
                    "state": False,
                    "time": end_time - start_time,
                    "msg": str(ex),
                }
            ]
        except Exception as e:
            end_time = time.time()
            tasks = [
                {
                    "name": "download_user_data",
                    "state": False,
                    "time": end_time - start_time,
                    "msg": str(e),
                }
            ]
        else:
            # response["userlist"] 只含  'department', 'userid' 2个字段
            if response["errcode"] == 0:
                # 1. 合并多部门
                dept_user = response["dept_user"]
                d = defaultdict(lambda : defaultdict(list))
                for dic in dept_user:
                    userid, department = dic["userid"], dic["department"]
                    d[userid]["userid"] = userid
                    d[userid]["department"].extend(str(department))

                userlist = []
                for key, value in d.items():
                    dept_user = {}
                    department = []
                    userid = value["userid"]
                    departments = value["department"]
                    for dep in departments:
                        department.append(int(dep))
                    userlist.append({"userid": userid, "department": department})

                # 2.下载用户
                if userlist:
                    for wecom_user in userlist:
                        download_user_result = self.download_user(company, wecom_user)
                        if download_user_result:
                            for r in download_user_result:
                                tasks.append(r)  # 加入 下载员工失败结果

                # 3.完成下载
                end_time = time.time()
                task = {
                    "name": "download_user_data",
                    "state": True,
                    "time": end_time - start_time,
                    "msg": _("User list sync completed."),
                }
                tasks.append(task)
        finally:
            return tasks  # 返回结果

    def download_user(self, company, wecom_user):
        """
        下载用户
        """
        user = self.sudo().search(
            [
                ("userid", "=", wecom_user["userid"]),
                ("company_id", "=", company.id),
            ],
            limit=1,
        )
   
        result = {}
        if not user:
            result = self.create_user(company, user, wecom_user)
        else:
            result = self.update_user(company, user, wecom_user)
        return result

    def create_user(self, company, user, wecom_user):
        """
        创建用户
        """
        try:
            user.create(
                {
                    "userid": wecom_user["userid"],
                    "department": wecom_user["department"],
                    "company_id": company.id,
                }
            )
        except Exception as e:
            result = _(
                "Error creating company [%s]'s user [%s], error reason: %s"
            ) % (
                company.userid,
                wecom_user["userid"].lower(),
                repr(e),
            )

            _logger.warning(result)
            return {
                "name": "add_user",
                "state": False,
                "time": 0,
                "msg": result,
            }

    def update_user(self, company, user, wecom_user):
        """
        更新用户
        """
        try:
            user.sudo().write(
                {
                    "department": wecom_user["department"],
                }
            )

        except Exception as e:
            result = _("Error update company [%s]'s user [%s], error reason: %s") % (
                company.name,
                wecom_user["userid"].lower(),
                repr(e),
            )
            _logger.warning(result)
            return {
                "name": "update_user",
                "state": False,
                "time": 0,
                "msg": result,
            }  # 返回失败结果

    def download_single_user(self):
        """
        下载单个用户
        """
        company = self.company_id
        params = {}
        message = ""
        try:
            wxapi = self.env["wecom.service_api"].InitServiceApi(
                company.corpid, company.contacts_app_id.secret
            )
            response = wxapi.httpCall(
                self.env["wecom.service_api_list"].get_server_api_call("USER_GET"),
                {"userid": self.userid},
            )
            for key in response.keys():
                if type(response[key]) in (list, dict) and response[key]:
                    json_str = json.dumps(
                        response[key],
                        sort_keys=False,
                        indent=2,
                        separators=(",", ":"),
                        ensure_ascii=False,
                    )
                    response[key] = json_str
            self.write(
                {
                    "name": response["name"],
                    "english_name": self.env["wecom.tools"].check_dictionary_keywords(
                        response, "english_name"
                    ),
                    "mobile": response["mobile"],
                    "department": response["department"],
                    "main_department": response["main_department"],
                    "order": response["order"],
                    "position": response["position"],
                    "gender": response["gender"],
                    "email": response["email"],
                    "biz_mail": response["biz_mail"],
                    "is_leader_in_dept": response["is_leader_in_dept"],
                    "direct_leader": response["direct_leader"],
                    "avatar": response["avatar"],
                    "thumb_avatar": response["thumb_avatar"],
                    "telephone": response["telephone"],
                    "alias": response["alias"],
                    "extattr": response["extattr"],
                    "external_profile": self.env[
                        "wecom.tools"
                    ].check_dictionary_keywords(response, "external_profile"),
                    "external_position": self.env[
                        "wecom.tools"
                    ].check_dictionary_keywords(response, "external_position"),
                    "status": response["status"],
                    "qr_code": response["qr_code"],
                    "address": self.env["wecom.tools"].check_dictionary_keywords(
                        response, "address"
                    ),
                    "open_userid": self.env["wecom.tools"].check_dictionary_keywords(
                        response, "open_userid"
                    ),
                }
            )
        except ApiException as ex:
            message = _("User [id:%s, name:%s] failed to download,Reason: %s") % (
                self.userid,
                self.name,
                str(ex),
            )
            _logger.warning(message)
            params = {
                "title": _("Download failed!"),
                "message": message,
                "sticky": True,  # 延时关闭
                "className": "bg-danger",
                "type": "danger",
            }
        else:
            message = _("User [id:%s, name:%s] downloaded successfully") % (
                self.userid,
                self.name,
            )
            params = {
                "title": _("Download Success!"),
                "message": message,
                "sticky": False,  # 延时关闭
                "className": "bg-success",
                "type": "success",
                "next": {
                    "type": "ir.actions.client",
                    "tag": "reload",
                },  # 刷新窗体
            }
        finally:
            action = {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": params,
            }
            return action

    def get_open_userid(self):
        """
        获取企微 open_userid
        """
        for user in self:
            try:
                wxapi = self.env["wecom.service_api"].InitServiceApi(
                    user.company_id.corpid,
                    user.company_id.contacts_app_id.secret,
                )
                response = wxapi.httpCall(
                    self.env["wecom.service_api_list"].get_server_api_call(
                        "USERID_TO_OPENID"
                    ),
                    {
                        "userid": user.userid,
                    },
                )
            except ApiException as ex:
                self.env["wecomapi.tools.action"].ApiExceptionDialog(
                    ex, raise_exception=True
                )
            else:
                user.open_userid = response["openid"]

    # ------------------------------------------------------------
    # 企微通讯录事件
    # ------------------------------------------------------------
    def wecom_event_change_contact_user(self, cmd):
        """
        通讯录事件变更成员
        """
        xml_tree = self.env.context.get("xml_tree")
        company_id = self.env.context.get("company_id")
        user_dict = xmltodict.parse(xml_tree)["xml"]
        # print("wecom_event_change_contact_user", user_dict)
        domain = [
            "|",
            ("active", "=", True),
            ("active", "=", False),
        ]

        users = self.sudo().search([("company_id", "=", company_id.id)] + domain)
        callback_user = users.search(
            [("userid", "=", user_dict["UserID"])],
            limit=1,
        )

        if callback_user:
            # 如果存在，则更新
            # 用于退出企业微信又重新加入企业微信的员工
            cmd = "update"
        else:
            # 如果不存在，停止
            return

        update_dict = {}

        for key, value in user_dict.items():
            if key.lower() in self._fields.keys():
                update_dict.update({key.lower(): value})
            else:
                if key == "MainDepartment":
                    update_dict.update({"main_department": value})
                elif key == "IsLeaderInDept":
                    update_dict.update({"is_leader_in_dept": value})
                elif key == "DirectLeader":
                    update_dict.update({"direct_leader": value})
                elif key == "BizMail":
                    update_dict.update({"biz_mail": value})
        if cmd == "create":
            update_dict.update({"company_id": company_id.id})
            callback_user.create(update_dict)
        elif cmd == "update":
            if "userid" in update_dict:
                del update_dict["userid"]
            callback_user.write(update_dict)
        elif cmd == "delete":
            callback_user.write(
                {
                    "active": False,
                }
            )

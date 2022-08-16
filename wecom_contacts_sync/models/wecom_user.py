# -*- coding: utf-8 -*-

import logging
import json
import time
from odoo import fields, models, api, Command, tools, _
from odoo.exceptions import UserError
from lxml import etree
# from lxml_to_dict import lxml_to_dict
from xmltodict import lxml_to_dict
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException
from odoo.addons.base.models.ir_mail_server import MailDeliveryException

_logger = logging.getLogger(__name__)


class WecomUser(models.Model):
    _name = "wecom.user"
    _description = "Wecom user"
    _order = "order_in_department"

    # 企微字段
    userid = fields.Char(
        string="User ID", readonly=True, default="",
    )  # 成员UserID。对应管理端的帐号
    name = fields.Char(string="Name", readonly=True, default="")  # 成员名称
    english_name = fields.Char(
        string="English name", readonly=True, default=""
    )  # 英部门文名称
    mobile = fields.Char(string="mobile phone", readonly=True, default="")  # 手机号码
    department = fields.Char(
        string="Multiple Departments", readonly=True, default=""
    )  # 成员所属部门id列表

    main_department = fields.Char(
        string="Main department", readonly=True, default=""
    )  # 主部门
    order = fields.Char(
        string="Sequence", readonly=True, default=""
    )  # 部门内的排序值，默认为0。数量必须和department一致，数值越大排序越前面。值范围是[0, 2^32)
    position = fields.Char(string="Position", readonly=True, default="")  # 职务信息；
    gender = fields.Char(
        string="Gender", readonly=True, default=""
    )  # 性别。0表示未定义，1表示男性，2表示女性。
    email = fields.Char(string="Email", readonly=True, default="")  # 邮箱
    biz_mail = fields.Char(string="BizMail", readonly=True, default="")  # 企业邮箱
    is_leader_in_dept = fields.Char(
        string="Is Department Leader", readonly=True, default=False
    )  # 表示在所在的部门内是否为部门负责人。0-否；1-是。是一个列表，数量必须与department一致。
    direct_leader = fields.Char(
        string="Direct Leader", readonly=True, default=""
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
        string="Open userid", readonly=True, default=""
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
        string="Sequence in department", readonly=True, default="0",
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
        compute="_compute_status_name",
    )  # 激活状态: 1=已激活，2=已禁用，4=未激活，5=退出企业。已激活代表已激活企业微信或已关注微信插件（原企业号）。未激活代表既未激活企业微信又未关注微信插件（原企业号）。

    gender_name = fields.Selection(
        [("1", _("Male")), ("2", _("Female")), ("0", _("Undefined"))],
        string="Gender",
        compute="_compute_gender_name",
    )
    color = fields.Integer("Color Index")

    @api.depends("status")
    def _compute_status_name(self):
        for user in self:
            user.status_name = str(user.status)

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
            # department_ids = self.env["wecom.department"].search(
            #     [
            #         ("department_id", "in", department_list),
            #         ("company_id", "=", user.company_id.id),
            #     ],
            # )

            user.write({"department_ids": [(6, 0, department_ids)]})

    def get_parent_department(self, company, departments):
        """
        获取上级部门
        """
        department_ids = []
        for department in departments:
            department_id = self.env["wecom.department"].search(
                [("department_id", "=", department), ("company_id", "=", company.id),],
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

            # 2020-8-10 按照官方API要求，进行重构
            response = wxapi.httpCall(
                self.env["wecom.service_api_list"].get_server_api_call(
                    "USER_SIMPLE_LIST"
                ),
                {"department_id": "1", "fetch_child": "1",},
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
            # response["userlist"] 只含 'name', 'department', 'userid' 三个字段
            wecom_users = response["userlist"]
            # 1.下载用户
            for wecom_user in wecom_users:
                download_user_result = self.download_user(company, wecom_user)
                if download_user_result:
                    for r in download_user_result:
                        tasks.append(r)  # 加入 下载员工失败结果

            # 2.完成下载
            end_time = time.time()
            task = {
                "name": "download_user_data",
                "state": True,
                "time": end_time - start_time,
                "msg": _("User list downloaded successfully."),
            }
            tasks.append(task)
        finally:
            return tasks  # 返回结果

    def download_user(self, company, wecom_user):
        """
        下载用户
        """
        user = self.sudo().search(
            [("userid", "=", wecom_user["userid"]), ("company_id", "=", company.id),],
            limit=1,
        )
        result = {}
        try:
            wxapi = self.env["wecom.service_api"].InitServiceApi(
                company.corpid, company.contacts_app_id.secret
            )

            response = wxapi.httpCall(
                self.env["wecom.service_api_list"].get_server_api_call("USER_GET"),
                {"userid": wecom_user["userid"]},
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

        except ApiException as ex:
            result = _(
                "Wecom API acquisition company[%s]'s user [id:%s] details failed, error details: %s"
            ) % (company.name, wecom_user["id"], str(ex))
            _logger.warning(result)
        except Exception as e:
            result = _(
                "Wecom API acquisition company[%s]'s user [id:%s] details failed, error details: %s"
            ) % (company.name, wecom_user["id"], str(e))
            _logger.warning(result)
        else:
            if not user:
                result = self.create_user(company, user, response)
            else:
                result = self.update_user(company, user, response)
        finally:
            return result

    def create_user(self, company, user, response):
        """
        创建用户
        """
        try:
            user.create(
                {
                    "userid": response["userid"],
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
                    "company_id": company.id,
                }
            )
        except Exception as e:
            result = _(
                "Error creating company [%s]'s user [%s,%s], error reason: %s"
            ) % (company.name, response["userid"].lower(), response["name"], repr(e),)

            _logger.warning(result)
            return {
                "name": "add_user",
                "state": False,
                "time": 0,
                "msg": result,
            }

    def update_user(self, company, user, response):
        """
        更新用户
        """
        try:
            user.write(
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

        except Exception as e:
            result = _("Error update company [%s]'s user [%s,%s], error reason: %s") % (
                company.name,
                response["userid"].lower(),
                response["name"],
                repr(e),
            )

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
                "next": {"type": "ir.actions.client", "tag": "reload",},  # 刷新窗体
            }
        finally:
            action = {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": params,
            }
            return action

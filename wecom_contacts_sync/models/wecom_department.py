# -*- coding: utf-8 -*-

import logging
import json
import time
from odoo import fields, models, api, Command, tools, _
from odoo.exceptions import UserError
import xmltodict
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException
from odoo.addons.base.models.ir_mail_server import MailDeliveryException

_logger = logging.getLogger(__name__)


class WecomDepartment(models.Model):
    _name = "wecom.department"
    _description = "Wecom department"
    _order = "complete_name"

    # 企微字段
    department_id = fields.Integer(
        string="Department ID", readonly=True, default=0
    )  # 部门id
    name = fields.Char(string="Name", readonly=True, default="",compute="_compute_name",)  # 部门名称
    name_en = fields.Char(string="English name", readonly=True, default="")  # 英部门文名称
    department_leader = fields.Char(
        string="Department Leader", readonly=True, default="[]"
    )  # 部门负责人的UserID；第三方仅通讯录应用可获取
    parentid = fields.Integer(
        string="Parent department id",
        readonly=True,
        default=0,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]"
    )  # 父部门id。根部门为1
    order = fields.Integer(
        string="Sequence",
        readonly=True,
        default=0,
    )  # 在父部门中的次序值。order值大的排序靠前。值范围是[0, 2^32)

    # odoo字段
    company_id = fields.Many2one(
        "res.company",
        required=True,
        domain="[('is_wecom_organization', '=', True)]",
        copy=False,
        store=True,
    )
    parent_id = fields.Many2one(
        "wecom.department",
        string="Parent Department",
        index=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        store=True,
        compute="_compute_parent_id",
    )
    child_ids = fields.One2many(
        "wecom.department", "parentid", string="Child Departments"
    )

    complete_name = fields.Char(
        "Complete Name", compute="_compute_complete_name", recursive=True, store=True
    )
    department_leader_ids = fields.Many2many(
        "wecom.user",
        "user_department_rel",
        "tag_id",
        "user_id",
        string="Department Leader",
    )
    user_ids = fields.Many2many(
        "wecom.user",
        "wecom_user_department_rel",
        "department_id",
        "user_id",
        string="Members",
    )
    color = fields.Integer("Color Index")

    @api.depends("department_id","company_id")
    def _compute_name(self):
        for department in self:
            if not department.name:
                department.name = "%s:%s" % (department.company_id.name, department.department_id)

    @api.depends("parentid","company_id")
    def _compute_parent_id(self):
        for department in self:
            if department.parentid:
                parent_department = self.sudo().search(
                    [
                        ("department_id", "=", department.parentid),("company_id", "=", department.company_id.id)
                    ]
                )
                department.parent_id = parent_department.id

    @api.depends("name", "parent_id","company_id")
    def _compute_complete_name(self):
        for department in self:
            if department.parent_id:
                department.complete_name = "%s / %s" % (
                    department.parent_id.complete_name,
                    department.name,
                )
            else:
                department.complete_name = department.name

    # @api.onchange('parent_id')
    # def _onchange_parentid(self):
    #     for department in self:
    #         if department.parent_id:
    #             department.complete_name = "%s / %s" % (
    #                 department.parent_id.complete_name,
    #                 department.name,
    #             )

    # ------------------------------------------------------------
    # 企微部门下载
    # ------------------------------------------------------------
    @api.model
    def download_wecom_deps(self):
        """
        下载部门列表
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

            # 2022-08-10 按官方建议进行重构
            # 官方建议换用 获取子部门ID列表 与 获取单个部门详情 组合的方式获取部门
            response = wxapi.httpCall(
                self.env["wecom.service_api_list"].get_server_api_call(
                    "DEPARTMENT_SIMPLELIST"
                ),
            )
        except ApiException as ex:
            end_time = time.time()
            self.env["wecomapi.tools.action"].ApiExceptionDialog(
                ex, raise_exception=False
            )
            tasks = [
                {
                    "name": "download_department_data",
                    "state": False,
                    "time": end_time - start_time,
                    "msg": str(ex),
                }
            ]
        except Exception as e:
            end_time = time.time()
            tasks = [
                {
                    "name": "download_department_data",
                    "state": False,
                    "time": end_time - start_time,
                    "msg": str(e),
                }
            ]
        else:
            if response["errcode"] == 0:
                # 获取只有 'id' , 'parentid' , 'order' 字段的列表
                wecom_departments = response["department_id"]

                # 1.下载部门
                for wecom_department in wecom_departments:
                    download_department_result = self.download_department(
                        company, wecom_department
                    )
                    if download_department_result:
                        for r in download_department_result:
                            tasks.append(r)  # 加入 下载员工失败结果

                # 3.完成
                end_time = time.time()
                task = {
                    "name": "download_department_data",
                    "state": True,
                    "time": end_time - start_time,
                    "msg": _("Department list sync completed."),
                }
                tasks.append(task)
        finally:
            return tasks  # 返回结果

    def download_department(self, company, wecom_department):
        """
        下载部门
        """
        # 查询数据库是否存在相同的企业微信部门ID，有则更新，无则新建
        department = self.sudo().search(
            [
                ("department_id", "=", wecom_department["id"]),
                ("company_id", "=", company.id),
            ],
            limit=1,
        )

        result = {}        

        if not department:                
            result = self.create_department(company, department, wecom_department)
        else:
            result = self.update_department(company, department, wecom_department)
        return result

    def create_department(self, company, department, wecom_department):
        """
        创建部门
        """
        try:
            department.create(
                {
                    "department_id": wecom_department["id"],
                    "parentid": wecom_department["parentid"],
                    "order": wecom_department["order"],
                    "company_id": company.id,
                }
            )

        except Exception as e:
            result = _(
                "Error creating company [%s]'s department [%s], error reason: %s"
            ) % (
                company.name,
                wecom_department["id"],
                repr(e),
            )
            _logger.warning(result)
            return {
                "name": "add_department",
                "state": False,
                "time": 0,
                "msg": result,
            }

    def update_department(self, company, department, wecom_department):
        """
        更新部门
        """
        try:
            department.write(
                {
                    "parentid": wecom_department["parentid"],
                    "order": wecom_department["order"],
                }
            )
        except Exception as e:
            result = _("Error updating Department [%s], error details:%s") % (
                wecom_department["name"],
                str(e),
            )
            result = _(
                "Error update company [%s]'s Department [%s], error reason: %s"
            ) % (
                company.name,
                wecom_department["id"],
                repr(e),
            )
            _logger.warning(result)
            return {
                "name": "update_department",
                "state": False,
                "time": 0,
                "msg": result,
            }

    def set_parent_department(self, company):
        """[summary]
        由于json数据是无序的，故在同步到本地数据库后，需要设置新增企业微信部门的上级部门
        """
        params = self.env["ir.config_parameter"].sudo()
        debug = params.get_param("wecom.debug_enabled")

        departments = self.search([("company_id", "=", company.id)])

        results = []
        for department in departments:
            if department.parentid and department.parentid != 0:
                # 忽略 parentid 为 0的部门
                parent_department = self.get_parent_department_by_department_id(
                    department, company
                )

                try:
                    department.write(
                        {
                            "parent_id": parent_department.id,
                        }
                    )
                except Exception as e:
                    result = _(
                        "Error setting parent department for company [%s], Error details:%s"
                    ) % (company.name, repr(e))
                    if debug:
                        _logger.warning(result)
                    results.append(
                        {
                            "name": "set_parent_department",
                            "state": False,
                            "time": 0,
                            "msg": result,
                        }
                    )
        return results  # 返回失败的结果

    def get_parent_department_by_department_id(self, department, company):
        """[summary]
        通过企微部门id 获取上级部门
        Args:
            department ([type]): [description]
            departments ([type]): [descriptions]
        """
        parent_department = self.search(
            [
                ("department_id", "=", department.parentid),
                ("company_id", "=", company.id),
            ]
        )
        return parent_department

    def download_single_department(self):
        """
        下载单个部门
        """
        company = self.company_id
        params = {}
        message = ""
        try:
            wxapi = self.env["wecom.service_api"].InitServiceApi(
                company.corpid, company.contacts_app_id.secret
            )
            response = wxapi.httpCall(
                self.env["wecom.service_api_list"].get_server_api_call(
                    "DEPARTMENT_DETAILS"
                ),
                {"id": str(self.department_id)},
            )
            department = response["department"]
            for key in department.keys():
                if type(department[key]) in (list, dict) and department[key]:
                    json_str = json.dumps(
                        department[key],
                        sort_keys=False,
                        indent=2,
                        separators=(",", ":"),
                        ensure_ascii=False,
                    )
                    department[key] = json_str
            self.sudo().write(
                {
                    "name": department["name"],
                    "name_en": self.env["wecom.tools"].check_dictionary_keywords(
                        department, "name_en"
                    ),
                    "department_leader": department["department_leader"],
                    "parentid": department["parentid"],
                    "order": department["order"],
                }
            )
        except ApiException as ex:
            message = _("Department [id:%s, name:%s] failed to download,Reason: %s") % (
                self.department_id,
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
        except Exception as e:
            message = _("Department [id:%s, name:%s] failed to download,Reason: %s") % (
                self.department_id,
                self.name,
                str(e),
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
            message = _("Department [id:%s, name:%s] downloaded successfully") % (
                self.department_id,
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

    # ------------------------------------------------------------
    # 企微通讯录事件
    # ------------------------------------------------------------
    def wecom_event_change_contact_party(self, cmd):
        xml_tree = self.env.context.get("xml_tree")
        company_id = self.env.context.get("company_id")
        department_dict = xmltodict.parse(xml_tree)["xml"]
 

        departments = self.sudo().search([("company_id", "=", company_id.id)])
        callback_department = departments.search(
            [("department_id", "=", department_dict["Id"])],
            limit=1,
        )
        update_dict = {}

        for key, value in department_dict.items():
            if key.lower() in self._fields.keys():
                update_dict.update({key.lower(): value})
            else:
                if key == "Id":
                    update_dict.update({"department_id": value})

        if "parentid" in update_dict:
            parent_id = departments.search(
                [("department_id", "=", update_dict["parentid"])],
                limit=1,
            ).id
            update_dict.update({"parent_id": parent_id})

        if cmd == "create":
            callback_department.create(update_dict)
        elif cmd == "update":
            if "department_id" in update_dict:
                del update_dict["department_id"]
            callback_department.write(update_dict)
        elif cmd == "delete":
            callback_department.unlink()

# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import Warning
import time
import logging
import json
from ...wxwork_api.wx_qy_api.CorpApi import *


_logger = logging.getLogger(__name__)


class HrDepartment(models.Model):

    _inherit = "hr.department"

    # _order = "wxwork_department_id"

    wxwork_department_id = fields.Integer(
        string="Enterprise WeChat department ID",
        readonly=True,
        translate=True,
        default="0",
    )
    # wxwork_employee_ids = fields.One2many(
    #     "hr.employee", "department_id", string="Enterprise WeChat Employees",
    # )
    wxwork_department_parent_id = fields.Integer(
        "Enterprise WeChat parent department ID",
        help="Parent department ID,32-bit integer.Root department is 1",
        readonly=True,
        translate=True,
    )
    wxwork_department_order = fields.Char(
        "Enterprise WeChat department sort",
        default="1",
        help="Order value in parent department. The higher order value is sorted first. The value range is[0, 2^32)",
        readonly=True,
        translate=True,
    )
    is_wxwork_department = fields.Boolean(
        string="Enterprise WeChat Department",
        readonly=True,
        translate=True,
        default=False,
    )


class SyncDepartment(models.Model):
    
    _inherit = "hr.department"

    def get_all_wxwrok_department_list(self):

        all_departments = self.sudo().search(
            ["|", ("active", "=", True), ("active", "=", False),],
        )

        departments_info = all_departments.sudo().read(
            ["id", "name", "complete_name", "wxwork_department_id"]
        )

        print(departments_info)
        wxwork_department_list = []

        # if departments:
        #     print("有数据")
        #     wxwork_department_list = [
        #         {"name": department.browse(department.id).name}
        #         for department in departments
        #     ]

        return wxwork_department_list

    def sync_department(self):
        params = self.env["ir.config_parameter"].sudo()
        corpid = params.get_param("wxwork.corpid")
        secret = params.get_param("wxwork.contacts_secret")
        debug = params.get_param("wxwork.debug_enabled")

        odoo_department_list = self.get_all_wxwrok_department_list()
        print(odoo_department_list)
        # odoo_departments = self.search(
        #     ["|", ("active", "=", False), ("active", "=", True),]
        # )
        # print(odoo_departments[0]["name"])
        # odoo_department_list = dict(
        #     (odoo_department["wxwork_department_id"][0])
        #     for odoo_department in odoo_departments
        # )
        # print(odoo_department_list)
        # for department in odoo_department_list:
        #     # wxwork_department_id = department.wxwork_department_id
        #     print(department)
        # odoo_department_list.insert({"id": department.id})

        sync_department_id = params.get_param("wxwork.contacts_sync_hr_department_id")

        # if debug:
        #     # _logger.info(
        #     #     _(
        #     #         "Start to synchronize Enterprise WeChat Contact - Department Synchronization"
        #     #     )
        #     # )
        #     _logger.info(
        #         "Start to synchronize Enterprise WeChat Contact - Department Synchronization"
        #     )
        # wxapi = CorpApi(corpid, secret)

        # try:
        #     response = wxapi.httpCall(
        #         CORP_API_TYPE["DEPARTMENT_LIST"], {"id": sync_department_id,},
        #     )

        #     start1 = time.time()
        #     wxwork_department_list = response["department"]
        #     for wxwork_department in wxwork_department_list:
        #         self.run_sync(wxwork_department, debug)
        #     end1 = time.time()
        #     times1 = end1 - start1

        #     start2 = time.time()
        #     # self.run_set(debug)

        #     end2 = time.time()
        #     times2 = end2 - start2

        #     times = times1 + times2
        #     # result = _("Department synchronization successful")
        #     result = "Department synchronization successful"
        #     status = {"department": str(True)}

        # except Exception as e:
        #     print(e)
        #     times = time.time()
        #     # result = _("Department synchronization failed")
        #     result = "Department synchronization failed"
        #     status = {"department": str(False)}
        #     if debug:
        #         # print(_("Department synchronization failed, error: %s", e))
        #         print("Department synchronization failed, error: %s" % e)
        # times = times
        # if debug:
        #     # _logger.info(
        #     #     _(
        #     #         "End sync Enterprise WeChat Contact - Department Synchronization,Total time spent: %s seconds",
        #     #         times,
        #     #     )
        #     # )
        #     _logger.info(
        #         "End sync Enterprise WeChat Contact - Department Synchronization,Total time spent: %s seconds"
        #         % times,
        #     )
        #     # print(times, type(times))
        #     # print(status, type(status))
        #     # print(result, type(result))
        # return times, status, result

    @api.model
    def run_sync(self, wxwork_department, debug):
        """
        执行同步部门
        """

        # 查询数据库是否存在相同的企业微信部门ID，有则更新，无则新建

        department = (
            self.env["hr.department"]
            .sudo()
            .search(
                [
                    # ("name", "=", wxwork_department["name"]),
                    "|",
                    ("active", "=", True),
                    ("active", "=", False),
                ],
                # limit=1,
            )
        )

        print(department)
        # print(odoo_department_list)
        # department = self.search(domain)

        # if not department:
        #     print("不存在部门: %s" % wxwork_department["name"])
        #     # self.create_department(department, wxwork_department, debug)
        # else:
        #     print("存在部门")

        # self.update_department(department, obj, debug)

        # try:
        #     if len(department) > 0:
        #         _logger.info("存在部门")
        #         self.update_department(department, obj, debug)
        #     else:
        #         _logger.info("不存在部门")
        #         self.create_department(department, obj, debug)
        # except Exception as e:
        #     if debug:
        #         print(repr(e))

        # with api.Environment.manage():
        #     new_cr = self.pool.cursor()
        #     self = self.with_env(self.env(cr=new_cr))
        #     env = self.sudo().env["hr.department"]
        #     print(" 查找数据")
        #     # 查询数据库是否存在相同的企业微信部门ID，有则更新，无则新建
        #     records = env.search(
        #         domain
        #         + [
        #             ("wxwork_department_id", "=", obj["id"]),
        #             ("is_wxwork_department", "=", True),
        #         ],
        #         limit=1,
        #     )
        #     print(" 判断")
        #     try:
        #         if len(records) > 0:
        #             print("更新部门")
        #             self.update_department(records, obj, debug)
        #         else:
        #             print("创建部门")
        #             self.create_department(records, obj, debug)
        #     except Exception as e:
        #         if debug:
        #             print(repr(e))

        #     new_cr.commit()
        #     new_cr.close()

    def create_department(self, records, obj, debug):
        try:
            records.create(
                {
                    "name": obj["name"],
                    "wxwork_department_id": int(obj["id"]),
                    "wxwork_department_parent_id": obj["parentid"],
                    "wxwork_department_order": obj["order"],
                    "is_wxwork_department": True,
                }
            )
            result = True
        except Exception as e:
            if debug:
                # print(_("department: %s - %s") % (obj["name"], repr(e)))
                print("department: %s - %s") % (obj["name"], e)
            result = False
        return result

    def update_department(self, records, obj, debug):
        try:
            records.write(
                {
                    "name": obj["name"],
                    "wxwork_department_parent_id": obj["parentid"],
                    "wxwork_department_order": obj["order"],
                    "is_wxwork_department": True,
                }
            )
            result = True
        except Exception as e:
            if debug:
                print(_("department:%s - %s") % (obj["name"], repr(e)))
            result = False
        return result

    def run_set(self, debug):
        """由于json数据是无序的，故在同步到本地数据库后，需要设置新增企业微信部门的上级部门"""
        result = True
        departments = self.search([("is_wxwork_department", "=", True),])
        try:
            for department in departments:
                if not department.wxwork_department_id:
                    pass
                else:
                    department.write(
                        {
                            "parent_id": self.get_parent_department(
                                department, departments
                            ).id,
                        }
                    )
            result = True
        except Exception as e:
            # if debug:
            #     print( _("Department: The parent department setting of %s failed")% (department.name, repr(e))
            if debug:
                print(
                    _("Department: The parent department setting of %s failed")
                    % repr(e)
                )
            result = False
        return result

        # with api.Environment.manage():
        #     new_cr = self.pool.cursor()
        #     self = self.with_env(self.env(cr=new_cr))
        #     env = self.sudo().env["hr.department"]
        #     departments = env.search([("is_wxwork_department", "=", True)])
        #     try:
        #         for dep in departments:
        #             if not dep.wxwork_department_id:
        #                 pass
        #             else:
        #                 dep.write(
        #                     {
        #                         "parent_id": self.get_parent_department(
        #                             dep, departments
        #                         ).id,
        #                     }
        #                 )
        #         result = True
        #     except BaseException as e:
        #         if debug:
        #             print(
        #                 _("Department: The parent department setting of %s failed")
        #                 % (dep.name, repr(e))
        #             )
        #         result = False
        #     new_cr.commit()
        #     new_cr.close()

        # return result

    def get_parent_department(self, department, departments):
        """
        获取上级部门
        """
        parent_department = departments.search(
            [
                ("wxwork_department_id", "=", department.wxwork_department_parent_id),
                ("is_wxwork_department", "=", True),
            ]
        )
        return parent_department

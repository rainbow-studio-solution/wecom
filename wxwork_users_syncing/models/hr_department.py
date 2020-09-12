# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import time
import logging

from ...wxwork_api.CorpApi import *


_logger = logging.getLogger(__name__)


class HrDepartment(models.Model):
    _inherit = "hr.department"
    _description = "Enterprise WeChat Department"
    _order = "wxwork_department_id"

    # name = fields.Char('微信部门名称',help='长度限制为1~32个字符，字符不能包括\:?”<>｜')
    wxwork_department_id = fields.Integer(
        "Enterprise WeChat department ID",
        default=0,
        help="Enterprise WeChat department ID",
        readonly=True,
        translate=True,
    )
    wxwork_department_parent_id = fields.Integer(
        "Enterprise WeChat parent department ID",
        default=1,
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
        "Enterprise WeChat Department", readonly=True, translate=True
    )


class SyncDepartment(models.Model):
    _inherit = "hr.department"
    _description = "Sync Enterprise WeChat Department"

    # @api.multi
    def sync_department(self):
        params = self.env["ir.config_parameter"].sudo()
        corpid = params.get_param("wxwork.corpid")
        secret = params.get_param("wxwork.contacts_secret")
        debug = params.get_param("wxwork.debug_enabled")
        sync_department_id = params.get_param("wxwork.contacts_sync_hr_department_id")
        if debug:
            _logger.error(
                _(
                    "Start to synchronize Enterprise WeChat Contact - Department Synchronization"
                )
            )
        wxapi = CorpApi(corpid, secret)
        # lock = Lock()
        try:
            response = wxapi.httpCall(
                CORP_API_TYPE["DEPARTMENT_LIST"],
                {
                    "id": sync_department_id,
                },
            )
            start1 = time.time()
            for obj in response["department"]:
                self.run_sync(obj, debug)
            end1 = time.time()
            times1 = end1 - start1

            start2 = time.time()
            self.run_set(debug)

            end2 = time.time()
            times2 = end2 - start2

            times = times1 + times2
            result = _("Department synchronization is successful, it takes time")
            status = {"department": True}
        except BaseException as e:
            times = time.time()
            result = _("Department synchronization failed, taking time")
            status = {"department": False}
            print(repr(e))
        times = times
        if debug:
            _logger.error(
                _(
                    "End sync Enterprise WeChat Contact - Department Synchronization,Total time spent: %s seconds"
                )
                % times
            )
        return times, status, result

    def run_sync(self, obj, debug):
        with api.Environment.manage():
            new_cr = self.pool.cursor()
            self = self.with_env(self.env(cr=new_cr))
            env = self.sudo().env["hr.department"]
            # 查询数据库是否存在相同的企业微信部门ID，有则更新，无则新建
            records = env.search(
                [
                    ("wxwork_department_id", "=", obj["id"]),
                    ("is_wxwork_department", "=", True),
                ],
                limit=1,
            )
            try:
                if len(records) > 0:
                    self.update_department(records, obj, debug)
                else:
                    self.create_department(records, obj, debug)
            except Exception as e:
                if debug:
                    print(repr(e))

            new_cr.commit()
            new_cr.close()

    def create_department(self, records, obj, debug):
        try:
            records.create(
                {
                    "name": obj["name"],
                    "wxwork_department_id": obj["id"],
                    "wxwork_department_parent_id": obj["parentid"],
                    "wxwork_department_order": obj["order"],
                    "is_wxwork_department": True,
                }
            )
            result = True
        except Exception as e:
            if debug:
                print(_("department: %s - %s") % (obj["name"], repr(e)))
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

        with api.Environment.manage():
            new_cr = self.pool.cursor()
            self = self.with_env(self.env(cr=new_cr))
            env = self.sudo().env["hr.department"]
            departments = env.search([("is_wxwork_department", "=", True)])
            try:
                for dep in departments:
                    if not dep.wxwork_department_id:
                        pass
                    else:
                        dep.write(
                            {
                                "parent_id": self.get_parent_department(
                                    dep, departments
                                ).id,
                            }
                        )
                result = True
            except BaseException as e:
                if debug:
                    print(
                        _("Department: The parent department setting of %s failed")
                        % (dep.name, repr(e))
                    )
                result = False
            new_cr.commit()
            new_cr.close()

            return result

    def get_parent_department(self, dep, departments):
        parent_department = departments.search(
            [
                ("wxwork_department_id", "=", dep.wxwork_department_parent_id),
                ("is_wxwork_department", "=", True),
            ]
        )
        return parent_department

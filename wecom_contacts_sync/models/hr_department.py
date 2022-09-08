# -*- coding: utf-8 -*-

import logging
import base64
from pdb import _rstr
import time
from lxml import etree
from odoo import api, fields, models, _

from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException

_logger = logging.getLogger(__name__)



class Department(models.Model):
    _inherit = "hr.department"

    category_ids = fields.Many2many(
        "hr.employee.category",
        "department_category_rel",
        "dmp_id",
        "category_id",
        groups="hr.group_hr_manager",
        string="Tags",
    )

    wecom_department_id = fields.Integer(
        string="WeCom department ID", readonly=True, default="0",
    )

    wecom_department_parentid = fields.Integer(
        "WeCom parent department ID", readonly=True,
    )
    wecom_department_order = fields.Char(
        "WeCom department sort", default="1", readonly=True,
    )
    is_wecom_department = fields.Boolean(
        string="WeCom Department", readonly=True, default=False,
    )

    # ------------------------------------------------------------
    # 同步企微部门
    # ------------------------------------------------------------
    @api.model
    def sync_wecom_deps(self):
        """
        下载部门列表
        """
        start_time = time.time()
        tasks = {}
        if self.env.context.get('company_id'):
            company = self.env['res.company'].browse(self.env.context['company_id'])
        else:
            company = self.env.company


        wecom_deps = self.env['wecom.department'].search([('company_id','=',company.id)])

        app_config = self.env["wecom.app_config"].sudo()
        contacts_sync_hr_department_id = app_config.get_param(
            company.contacts_app_id.id, "contacts_sync_hr_department_id"
        )  # 需要同步的企业微信部门ID
        try:
            for wecom_dep in wecom_deps:
                # 从企业微信同步部门
                department = self.search([('wecom_department_id','=',wecom_dep.department_id)])
                if wecom_dep.department_id == 1:
                    # department_id ==1 为根部门,不需要同步
                    pass
                elif wecom_dep.department_id == int(contacts_sync_hr_department_id):
                    # contacts_sync_hr_department_id 不需要同步
                    pass
                else:
                    if not department:
                        department = self.sudo().create({
                            'company_id':company.id,
                            'name':wecom_dep.name,
                            'wecom_department_id':wecom_dep.department_id,
                            'wecom_department_parentid':0 if wecom_dep.parentid==1 else wecom_dep.parentid,
                            'is_wecom_department':True,
                        })
                    else:
                        department.sudo().write({
                            'wecom_department_id':wecom_dep.department_id,
                            'wecom_department_parentid':wecom_dep.parentid,
                        })
            # TODO: 设置上级部门
        except Exception as e:
            end_time = time.time()
            tasks = {
                "state": False,
                "time": end_time - start_time,
                "msg": str(e),
            }
        else:
            end_time = time.time()
            tasks = {
                "state": True,
                "time": end_time - start_time,
                "msg": _("Successfully synchronized wecom department"),
            }
        finally:
            return tasks

# -*- coding: utf-8 -*-

import logging
import time
from odoo import fields, models, api, Command, tools, _
from odoo.exceptions import UserError
from lxml import etree
from lxml_to_dict import lxml_to_dict
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException
from odoo.addons.base.models.ir_mail_server import MailDeliveryException

_logger = logging.getLogger(__name__)


class WecomDepartment(models.Model):
    _name = "wecom.department"
    _description = "Wecom department"
    _order = "order"

    
    # 企微字段
    department_id = fields.Integer(string="Department ID", readonly=True,default="0",) # 部门id
    name = fields.Char(string="Name", readonly=True,default="") # 部门名称
    name_en = fields.Char(string="English name", readonly=True,default="") # 英部门文名称
    department_leader = fields.Char(string="Department Leader", readonly=True,default="") # 部门负责人的UserID；第三方仅通讯录应用可获取
    parentid = fields.Integer(string="Superior department", readonly=True,default="0",) # 父部门id。根部门为1
    order = fields.Integer(string="Sequence", readonly=True,default="0",) # 在父部门中的次序值。order值大的排序靠前。值范围是[0, 2^32)

    # odoo字段
    company_id = fields.Many2one('res.company',required=True,domain="[('is_wecom_organization', '=', True)]",
        copy=False,
        store=True,)
    parent_id = fields.Many2one('wecom.department', string='Parent Department', index=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    child_ids = fields.One2many('wecom.department', 'parent_id', string='Child Departments')
    member_ids = fields.One2many('wecom.user', 'department_id', string='Members', readonly=True)

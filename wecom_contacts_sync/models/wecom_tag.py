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


class WecomTag(models.Model):
    _name = "wecom.tag"
    _description = "Wecom tag"

    company_id = fields.Many2one('res.company',required=True,domain="[('is_wecom_organization', '=', True)]",
        copy=False,
        store=True,)

    name = fields.Char(string="Name", readonly=True,default="") # 标签名称
    tagid = fields.Integer(string="Tag ID", readonly=True,default="0",) # 标签id
    tagname = fields.Char(string="Tag name", readonly=True,default="") # 标签名称
    userlist = fields.Text(string="User list", readonly=True,default="") # 标签中包含的成员列表
    partylist = fields.Text(string="Party list", readonly=True,default="") # 标签中包含的部门id列表
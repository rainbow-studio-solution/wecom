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


class WecomUser(models.Model):
    _name = "wecom.user"
    _description = "Wecom user"
    _order = "sort_in_Department"

    
    # 企微字段
    userid = fields.Char(string="User ID", readonly=True, default="",) # 成员UserID。对应管理端的帐号
    name = fields.Char(string="Name", readonly=True,default="") # 成员名称
    english_name = fields.Char(string="English name", readonly=True,default="") # 英部门文名称
    mobile = fields.Char(string="mobile phone", readonly=True,default="") # 手机号码
    department = fields.Char(string="Department", readonly=True,default="") # 成员所属部门id列表
    
    main_department = fields.Char(string="Main department", readonly=True,default="") # 主部门
    order = fields.Char(string="Sequence", readonly=True,default="") # 部门内的排序值，默认为0。数量必须和department一致，数值越大排序越前面。值范围是[0, 2^32)
    position = fields.Char(string="Position", readonly=True,default="") # 职务信息；
    gender = fields.Char(string="Gender", readonly=True,default="") # 性别。0表示未定义，1表示男性，2表示女性。
    email = fields.Char(string="Email", readonly=True,default="") # 邮箱
    biz_mail = fields.Char(string="BizMail", readonly=True,default="") # 企业邮箱
    is_leader_in_dept = fields.Boolean(string="Department Leader", readonly=True,default=False) # 表示在所在的部门内是否为部门负责人。0-否；1-是。是一个列表，数量必须与department一致。
    direct_leader = fields.Char(string="Direct Leader", readonly=True,default="")# 直属上级UserID，返回在应用可见范围内的直属上级列表，最多有五个直属上级
    avatar = fields.Char(string="Avatar", readonly=True,default="") # 头像url
    thumb_avatar = fields.Char(string="Avatar thumbnail", readonly=True,default="") # 头像缩略图url
    telephone = fields.Char(string="Telephone", readonly=True,default="") # 座机号码
    alias = fields.Char(string="Alias", readonly=True,default="") # 别名
    extattr = fields.Text(string="Extended attributes", readonly=True,default="") # 扩展属性
    external_profile = fields.Text(string="External attributes", readonly=True,default="") # 成员对外属性
    external_position = fields.Char(string="External position", readonly=True,default="") # 对外职务，如果设置了该值，则以此作为对外展示的职务，否则以position来展示。
    status = fields.Integer(string="Status", readonly=True,default="") # 激活状态: 1=已激活，2=已禁用，4=未激活，5=退出企业。已激活代表已激活企业微信或已关注微信插件（原企业号）。未激活代表既未激活企业微信又未关注微信插件（原企业号）。
    qr_code = fields.Char(string="Personal QR code", readonly=True,default="") # 员工个人二维码，扫描可添加为外部联系人
    address = fields.Char(string="Address", readonly=True,default="") # 地址
    open_userid = fields.Char(string="Open userid", readonly=True,default="") # 开放用户Id,全局唯一,对于同一个服务商，不同应用获取到企业内同一个成员的open_userid是相同的，最多64个字节。仅第三方应用可获取


    # odoo 字段
    company_id = fields.Many2one('res.company',required=True,domain="[('is_wecom_organization', '=', True)]",
        copy=False,
        store=True,)
    department_id = fields.Many2one('wecom.department', 'Department', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    sort_in_Department = fields.Integer(string="Sort in department", readonly=True,default="0",) # 成员在对应部门中的排序值，默认为0。数量必须和department一致
    status_name = fields.Selection( [
            ("1", _("Activated")),
            ("2", _("Disabled")),
            ("4", _("Not active")),
            ("5", _("Exit the enterprise")),
        ],string="Status", readonly=True, compute="_compute_status_name",) # 激活状态: 1=已激活，2=已禁用，4=未激活，5=退出企业。已激活代表已激活企业微信或已关注微信插件（原企业号）。未激活代表既未激活企业微信又未关注微信插件（原企业号）。

    @api.depends("status")
    def _compute_status_name(self):
        for user in self:
            user.status_name = str(user.status)
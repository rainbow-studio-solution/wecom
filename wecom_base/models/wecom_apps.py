# -*- coding: utf-8 -*-

from odoo import fields, models, _


class WeComApps(models.Model):
    _name = "wecom.apps"
    _description = "Wecom Application"
    _order = "sequence"

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        domain="[('is_wecom_organization', '=', True)]",
        copy=False,
        store=True,
    )

    type = fields.Selection(
        [
            ("manage", "Manage Tools"),
            ("base", "Base"),
            ("self", "Self built"),
            ("third", "Third party"),
        ],
        string="Application type",
        required=True,
        copy=True,
    )

    name = fields.Char(
        string="Name", required=True, translate=True, copy=True
    )  # 企业应用名称
    agentid = fields.Integer(string="Agent ID", copy=False)  # 企业应用id
    secret = fields.Char("Secret", default="", copy=False)
    square_logo_url = fields.Char(string="Square Logo", copy=False)  # 企业应用方形头像
    description = fields.Text(
        string="Description", translate=True, copy=False
    )  # 企业应用详情
    allow_userinfos = fields.Char(
        string="Visible range (personnel)", copy=False
    )  # 企业应用可见范围（人员），其中包括userid
    allow_partys = fields.Char(
        string="Visible range (Department)", copy=False
    )  # 企业应用可见范围（部门）
    allow_tags = fields.Char(string="Visible range (Tag))", copy=False)  # 企业应用可见范围（标签）
    close = fields.Boolean(string="Disabled", copy=False)  # 	企业应用是否被停用
    redirect_domain = fields.Char(string="Trusted domain name", copy=True)  # 企业应用可信域名
    report_location_flag = fields.Boolean(
        string="Open the geographic location and report", copy=False
    )  # 企业应用是否打开地理位置上报 0：不上报；1：进入会话上报；
    isreportenter = fields.Boolean(
        string="Report user entry event", copy=False
    )  # 企业应用是否打开进入会话上报 0：不上报；1：进入会话上报；
    home_url = fields.Char(string="Home page", copy=True)  # 企业应用主页url

    sequence = fields.Integer(default=0, copy=True)

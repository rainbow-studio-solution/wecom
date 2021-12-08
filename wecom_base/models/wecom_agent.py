# -*- coding: utf-8 -*-

from odoo import fields, models, _


class WeComAgent(models.Model):
    _name = "wecom.agent"
    _description = "Wecom Application"

    name = fields.Char(string="Name", required=True)  # 企业应用名称
    agentid = fields.Integer(string="Agent ID", required=True)  # 企业应用id
    square_logo_url = fields.Char(string="Square Logo")  # 企业应用方形头像
    description = fields.Char(string="Description")  # 企业应用详情
    allow_userinfos = fields.Char(
        string="Visible range (personnel)"
    )  # 企业应用可见范围（人员），其中包括userid
    allow_partys = fields.Char(string="Visible range (Department)")  # 企业应用可见范围（部门）
    allow_tags = fields.Char(string="Visible range (Tag))")  # 企业应用可见范围（标签）
    close = fields.Boolean(string="Disabled")  # 	企业应用是否被停用
    redirect_domain = fields.Char(string="Trusted domain name")  # 企业应用可信域名
    report_location_flag = fields.Boolean(
        string="Open the geographic location and report"
    )  # 企业应用是否打开地理位置上报 0：不上报；1：进入会话上报；
    isreportenter = fields.Boolean(
        string="Report user entry event"
    )  # 企业应用是否打开进入会话上报 0：不上报；1：进入会话上报；
    home_url = fields.Char(string="Home page")  # 企业应用主页url

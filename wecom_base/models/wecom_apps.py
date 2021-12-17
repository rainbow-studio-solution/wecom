# -*- coding: utf-8 -*-


from odoo import _, api, fields, models
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException
from odoo.exceptions import UserError


class WeComApps(models.Model):
    _name = "wecom.apps"
    _description = "Wecom Application"
    _order = "sequence"

    name = fields.Char(
        string="Name",
        copy=False,
        compute="_compute_name",
        store=True,
        index=True,
    )  # 企业应用名称
    app_name = fields.Char(
        string="Application Name",
        translate=True,
        copy=True,
    )  # 应用名称

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        domain="[('is_wecom_organization', '=', True)]",
        copy=False,
        store=True,
    )

    # 应用类型  required=True
    type = fields.Selection(
        selection=lambda self: self._type_selection_values(),
        string="Application Type",
        required=True,
        copy=True,
        default="manage",
    )
    type_id = fields.Many2one("wecom.app.type", string="Application Types", store=True)

    subtype_ids = fields.Many2many(
        "wecom.app.subtype",
        string="Application Subtype",
    )
    type_code = fields.Char(string="Application type code", store=True)

    @api.onchange("subtype_ids")
    def _onchange_subtype_ids(self):
        """
        变更子类型
        :return:
        """
        if self.type_id.code == "manage" or self.type_id.code == "base":
            if len(self.subtype_ids) > 1:
                raise UserError(
                    _("Only one subtype can be selected for the current app type!")
                )
        if self.subtype_ids:
            self.type_code = self.subtype_ids.mapped("code")
        else:
            self.type_code = []

    @api.model
    def _type_selection_values(self):
        models = self.env["wecom.app.type"].sudo().search([]).sorted("sequence")
        return [(model.code, model.name) for model in models]

    @api.onchange("type")
    def _onchange_type(self):
        self.subtype_ids = False
        self.type_code = ""
        if self.type:
            type = self.env["wecom.app.type"].sudo().search([("code", "=", self.type)])
            self.type_id = type
            return {"domain": {"subtype_ids": [("parent_id", "=", type.id)]}}
        else:
            self.type_id = False
            return {"domain": {"subtype": []}}

    agentid = fields.Integer(string="Agent ID", copy=False)  # 企业应用id
    secret = fields.Char("Secret", default="", copy=False)
    square_logo_url = fields.Char(string="Square Logo", copy=True)  # 企业应用方形头像
    description = fields.Text(string="Description", translate=True, copy=True)  # 企业应用详情
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

    # 访问令牌
    access_token = fields.Char(string="Access Token", readonly=True, copy=False)
    expiration_time = fields.Datetime(
        string="Expiration Time", readonly=True, copy=False
    )

    _sql_constraints = [
        (
            "company_id_key_uniq",
            "unique (company_id,app_name)",
            _("The application name of each company must be unique !"),
        )
    ]

    @api.depends("company_id", "app_name", "type")
    def _compute_name(self):
        for app in self:
            labels = dict(self.fields_get(allfields=["type"])["type"]["selection"])[
                app.type
            ]
            if app.company_id:
                app.name = "%s/%s/%s" % (
                    app.company_id.abbreviated_name,
                    labels,
                    app.app_name,
                )
            else:
                app.name = "%s/%s" % (labels, app.app_name)

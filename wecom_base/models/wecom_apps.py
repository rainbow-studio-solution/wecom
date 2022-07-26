# -*- coding: utf-8 -*-

import logging
import datetime
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException

_logger = logging.getLogger(__name__)


class WeComApps(models.Model):
    _name = "wecom.apps"
    _description = "Wecom Application"
    _order = "sequence"

    name = fields.Char(
        string="Name", copy=False, compute="_compute_name", store=True, index=True,
    )  # 企业应用名称
    app_name = fields.Char(
        string="Application Name", translate=True, copy=True,
    )  # 应用名称

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        domain="[('is_wecom_organization', '=', True)]",
        copy=False,
        store=True,
    )
    # model_ids = fields.Many2many("ir.model", string="Related Model",)
    # 应用类型  required=True
    type = fields.Selection(
        selection=lambda self: self._type_selection_values(),
        string="Application Type",
        required=True,
        copy=True,
        default="manage",
    )
    type_id = fields.Many2one("wecom.app.type", string="Application Types", store=True)

    subtype_ids = fields.Many2many("wecom.app.subtype", string="Application Subtype",)
    type_code = fields.Char(
        string="Application type code",
        store=True,
        readonly=True,
        compute="_computet_type_code",
    )

    def write(self, vals):
        for app in self:
            labels = dict(self.fields_get(allfields=["type"])["type"]["selection"])[
                app.type
            ]
            if "company_id" in vals:
                company = app.company_id
                vals["name"] = "%s/%s/%s" % (
                    company.abbreviated_name,
                    labels,
                    app.app_name,
                )
            else:
                vals["name"] = "%s/%s" % (labels, app.app_name)
        result = super(WeComApps, self).write(vals)

        return result

    @api.depends("subtype_ids")
    def _computet_type_code(self):
        """
        计算应用类型代码
        """
        if self.subtype_ids:
            self.type_code = str(self.subtype_ids.mapped("code"))
        else:
            self.type_code = "[]"

    def get_type_code(self):
        """
        测试代码
        """
        type_code = str(self.subtype_ids.mapped("code"))
        print(type_code, type(type_code))

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

    @api.model
    def _type_selection_values(self):
        models = self.env["wecom.app.type"].sudo().search([]).sorted("sequence")
        return [(model.code, model.name) for model in models]

    @api.onchange("type")
    def _onchange_type(self):
        # self.subtype_ids = False
        # self.type_code = ""
        # if self.type:
        #     type = self.env["wecom.app.type"].sudo().search([("code", "=", self.type)])
        #     self.type_id = type
        #     return {"domain": {"subtype_ids": [("parent_id", "=", type.id)]}}
        # else:
        #     self.type_id = False
        #     return {"domain": {"subtype": []}}
        if self.subtype_ids:
            self.type_code = str(self.subtype_ids.mapped("code"))
        else:
            self.type_code = "[]"

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
    menu_body = fields.Text(
        "Application menu data", translate=True, default="{}", copy=False,
    )

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

    @api.model_create_multi
    def create(self, values):
        res = super(WeComApps, self).create(values)
        if res.subtype_ids:
            res.type_code = str(res.subtype_ids.mapped("code"))
        else:
            res.type_code = "[]"
        return res

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

    # 回调服务
    app_callback_service_ids = fields.One2many(
        "wecom.app_callback_service",
        "app_id",
        string="Receive event service",
        domain="['|', ('active', '=', True), ('active', '=', False)]",
        context={"active_test": False},
    )

    # 应用参数配置
    app_config_ids = fields.One2many(
        "wecom.app_config",
        "app_id",
        string="Application Configuration",
        # context={
        #     "default_company_id": lambda self: self.company_id,
        # },
    )  # 应用参数配置

    # ————————————————————————————————————
    # 应用回调服务
    # ————————————————————————————————————
    def generate_service(self):
        """
        生成回调服务
        :return:
        """
        code = self.env.context.get("code")  # 按钮的传递值
        if bool(code):
            # 存在按钮的传递值，通过按钮的传递值生成回调服务
            self.generate_service_by_code(code)
        else:
            # 不存在按钮的传递值，通过子类型生成生成回调服务
            self.generate_service_by_subtype()

    def generate_service_by_subtype(self):
        """
        通过子类型生成生成回调服务
        """
        for record in self.subtype_ids:
            self.generate_service_by_code(record.code)

    def generate_service_by_code(self, code):
        """
        根据code生成回调服务
        :param code:
        :return:
        """

    # ————————————————————————————————————
    # 应用参数配置
    # ————————————————————————————————————
    def generate_parameters(self):
        """
        生成参数
        :return:
        """
        code = self.env.context.get("code")  # 按钮的传递值
        if bool(code):
            # 存在按钮的传递值，通过按钮的传递值生成回调服务
            self.generate_parameters_by_code(code)
        else:
            # 不存在按钮的传递值，通过子类型生成生成回调服务
            self.generate_parameters_by_subtype()

    def generate_parameters_by_subtype(self):
        """
        通过子类型生成生成参数
        """
        for record in self.subtype_ids:
            self.generate_parameters_by_code(record.code)

    def generate_parameters_by_code(self, code):
        """
        根据code生成参数
        :param code:
        :retur
        """

    # ————————————————————————————————————
    # 应用信息
    # ————————————————————————————————————

    def get_app_info(self):
        """
        获取企业应用信息
        :param agentid:
        :return:
        """
        for record in self:
            try:
                wecomapi = self.env["wecom.service_api"].InitServiceApi(
                    record.company_id.corpid, record.secret
                )
                response = wecomapi.httpCall(
                    self.env["wecom.service_api_list"].get_server_api_call("AGENT_GET"),
                    {"agentid": str(record.agentid)},
                )
            except ApiException as e:
                return self.env["wecomapi.tools.action"].ApiExceptionDialog(
                    e, raise_exception=True
                )
            else:
                if response["errcode"] == 0:
                    record.write(
                        {
                            "app_name": response["name"],
                            "square_logo_url": response["square_logo_url"],
                            "description": response["description"],
                            "allow_userinfos": response["allow_userinfos"]
                            if "allow_userinfos" in response
                            else "{}",
                            "allow_partys": response["allow_partys"]
                            if "allow_partys" in response
                            else "{}",
                            "allow_tags": response["allow_tags"]
                            if "allow_tags" in response
                            else "{}",
                            "close": response["close"],
                            "redirect_domain": response["redirect_domain"],
                            "report_location_flag": response["report_location_flag"],
                            "isreportenter": response["isreportenter"],
                            "home_url": response["home_url"],
                        }
                    )
                    # msg = {
                    #     "title": _("Tips"),
                    #     "message": _("Successfully obtained application information!"),
                    #     "sticky": False,
                    # }
                    # return self.env["wecomapi.tools.action"].WecomSuccessNotification(msg)

    def set_app_info(self):
        """
        设置企业应用信息
        :param agentid:
        :return:
        """

    # ————————————————————————————————————
    # 应用令牌
    # ————————————————————————————————————
    def get_access_token(self):
        """获取企业应用接口调用凭据（令牌）
        :return:
        """
        ir_config = self.env["ir.config_parameter"].sudo()
        debug = ir_config.get_param("wecom.debug_enabled")
        if debug:
            _logger.info(
                _("Start getting app [%s] token for company [%s]")
                % (self.name, self.company_id.name)
            )
        try:
            wecom_api = self.env["wecom.service_api"].InitServiceApi(
                self.company_id.corpid, self.secret
            )
        except ApiException as ex:
            return self.env["wecomapi.tools.action"].ApiExceptionDialog(
                ex, raise_exception=True
            )
        # finally:
        #     if self.expiration_time and self.expiration_time > datetime.now():
        #         # 令牌未过期，则直接返回 提示信息
        #         msg = {
        #             "title": _("Tips"),
        #             "message": _("Token is still valid, and no update is required!"),
        #             "sticky": False,
        #         }
        #         return self.env["wecomapi.tools.action"].WecomInfoNotification(msg)

    def cron_get_app_token(self):
        """
        自动任务定时获取应用token
        """
        for app in self.search([("company_id", "!=", False)]):
            _logger.info(
                _(
                    "Automatic task: start to get the application [%s] token of company [%s]"
                )
                % (app.name, app.company_id.name)
            )
            app.get_access_token()

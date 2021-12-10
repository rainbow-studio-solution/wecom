# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from odoo import _, api, fields, models
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException
from odoo.api import model_create_single


class WeComApps(models.Model):
    _inherit = "wecom.apps"

    def _default_callback_url(self):
        """
        默认回调地址
        :return:"""
        params = self.env["ir.config_parameter"].sudo()
        base_url = params.get_param("web.base.url")
        if self.company_id and self.callback_service:
            return base_url + "/wecom_callback/%s/%s" % (
                self.callback_service,
                self.company_id.id,
            )
        else:
            return ""

    # 接收事件服务器配置
    # https://work.weixin.qq.com/api/doc/90000/90135/90930
    callback_service = fields.Char(
        string="Callback Service Name",
        copy=True,
        help="Callback service name to facilitate finding applications in routing",
    )  # 回调服务地址代码，便于在路由中查找
    callback_url = fields.Char(
        string="Callback URL",
        store=True,
        readonly=True,
        default=_default_callback_url,
        copy=False,
    )  # 回调服务地址
    callback_url_token = fields.Char(
        string="Callback URL Token", copy=False
    )  # Token用于计算签名
    callback_aeskey = fields.Char(string="Callback AES Key", copy=False)  # 用于消息内容加密

    # 应用参数配置
    app_config_ids = fields.One2many(
        "wecom.app_config",
        "app_id",
        string="Application Configuration",
        # domain="[('app_id', '=', current_company_id)]",
    )  # 应用参数配置

    _sql_constraints = [
        (
            "callback_service_company_uniq",
            "unique (callback_service, company_id)",
            "The callback service name of each company is unique!",
        ),
    ]

    @api.onchange("company_id", "callback_service")
    def _onchange_callback_url(self):
        """
        当公司和服务名称发生变化时，更新回调服务地址
        :return:
        """
        params = self.env["ir.config_parameter"].sudo()
        base_url = params.get_param("web.base.url")

        if self.company_id and self.callback_service:
            self.callback_url = base_url + "/wecom_callback/%s/%s" % (
                self.callback_service,
                self.company_id.id,
            )
        else:
            self.callback_url = ""

    def get_app_info(self):
        """
        获取企业应用信息
        :param agentid:
        :return:
        """
        try:
            wecomapi = self.env["wecom.service_api"].InitServiceApi(
                self.company_id.corpid, self.secret
            )
            response = wecomapi.httpCall(
                self.env["wecom.service_api_list"].get_server_api_call("AGENT_GET"),
                {"agentid": str(self.agentid)},
            )
        except ApiException as e:
            return self.env["wecomapi.tools.action"].ApiExceptionDialog(
                e, raise_exception=True
            )
        else:
            if response["errcode"] == 0:
                self.write(
                    {
                        "name": response["name"],
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
                msg = {
                    "title": _("Tips"),
                    "message": _("Successfully obtained application information!"),
                    "sticky": False,
                }
                return self.env["wecomapi.tools.action"].ApiSuccessNotification(msg)

    def set_app_info(self):
        """
        设置企业应用信息
        :param agentid:
        :return:
        """

    def get_access_token(self):
        """ 获取企业应用接口调用凭据（令牌）
        :return:
        """
        try:
            wecomapi = self.env["wecom.service_api"].InitServiceApi(
                self.company_id.corpid, self.secret
            )

        except ApiException as ex:
            return self.env["wecomapi.tools.action"].ApiExceptionDialog(
                ex, raise_exception=True
            )
        else:
            if self.access_token is False:
                # 令牌为空，则获取
                self.access_token = wecomapi.access_token
                self.expiration_time = wecomapi.expiration_time
                msg = {
                    "title": _("Tips"),
                    "message": _("The access token was successfully obtained!"),
                    "sticky": False,
                }
                return self.env["wecomapi.tools.action"].ApiSuccessNotification(msg)
            elif wecomapi.expiration_time > datetime.now():
                # 令牌未过期，则直接返回 提示信息
                msg = {
                    "title": _("Tips"),
                    "message": _("Token is still valid, and no update is required!"),
                    "sticky": False,
                }
                return self.env["wecomapi.tools.action"].ApiInfoNotification(msg)
            else:
                # 令牌已过期，则重新获取
                self.access_token = wecomapi.access_token
                self.expiration_time = wecomapi.expiration_time
                msg = {
                    "title": _("Tips"),
                    "message": _("The access token was successfully obtained!"),
                    "sticky": False,
                }
                return self.env["wecomapi.tools.action"].ApiSuccessNotification(msg)

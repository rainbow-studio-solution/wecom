# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.wxwork_api.api.corp_api import CorpApi, CORP_API_TYPE
from odoo.addons.wxwork_api.api.wecom_abstract_api import ApiException
from odoo.addons.wxwork_api.api.error_code import Errcode

from datetime import datetime
import datetime

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )

    auth_agentid = fields.Char(related="company_id.auth_agentid", readonly=False)

    auth_secret = fields.Char(related="company_id.auth_secret", readonly=False)

    corp_jsapi_ticket = fields.Char(
        "Enterprise JS API Ticket",
        related="company_id.corp_jsapi_ticket",
        readonly=True,
    )

    agent_jsapi_ticket = fields.Char(
        "Application JS API Ticket",
        related="company_id.agent_jsapi_ticket",
        readonly=True,
    )

    jsapi_debug = fields.Boolean(
        "JS API Debug mode",
        config_parameter="wxwork.jsapi_debug",
        default=False,
    )

    js_api_list = fields.Char(
        "JS API Inertface List",
        related="company_id.js_api_list",
        readonly=False,
    )
    # js_api_list = fields.Selection(
    #     [
    #         ("selectEnterpriseContact", "选人接口"),
    #         ("openUserProfile", "打开个人信息页接口"),
    #         ("openUserProfile", "外部联系人选人接口"),
    #         ("selectExternalContact", "外部联系人选人接口"),
    #         ("getCurExternalContact", "获取当前外部联系人userid"),
    #         ("getCurExternalChat", "获取当前客户群的群ID"),
    #         ("sendChatMessage", "聊天工具栏分享消息到会话"),
    #         ("getContext", "聊天工具栏分享消息到会话"),
    #         ("openEnterpriseChat", "创建会话接口"),
    #         ("openEnterpriseChat", "创建会话接口"),
    #         ("onMenuShareAppMessage", "分享接口-获取“转发”按钮"),
    #         ("onMenuShareWechat", "分享接口-获取“微信”按钮"),
    #         ("onMenuShareTimeline", "分享接口-获取“分享到朋友圈”按钮"),
    #         ("shareAppMessage", "分享接口-自定义转发到会话"),
    #         ("shareWechatMessage", "分享接口-自定义转发到微信"),
    #         ("shareToExternalContact", "分享接口-将H5页面通过个人群发发送给客户"),
    #         ("shareToExternalChat", "分享接口-将H5页面通过群发助手发送给客户群"),
    #         ("onHistoryBack", "界面操作-监听页面返回事件"),
    #         ("hideOptionMenu", "界面操作-隐藏右上角菜单接口"),
    #         ("showOptionMenu", "界面操作-显示右上角菜单接口"),
    #         ("closeWindow", "界面操作-关闭当前网页窗口接口"),
    #         ("hideMenuItems", "界面操作-批量隐藏功能按钮接口"),
    #         ("showMenuItems", "界面操作-批量显示功能按钮接口"),
    #         ("hideAllNonBaseMenuItem", "界面操作-隐藏所有非基础按钮接口"),
    #         ("showAllNonBaseMenuItem", "界面操作-显示所有功能按钮接口"),
    #         ("openDefaultBrowser", "界面操作-打开系统默认浏览器"),
    #         ("onUserCaptureScreen", "界面操作-用户截屏事件"),
    #         ("scanQRCode", "企业微信扫一扫"),
    #         ("chooseInvoice", "电子发票-拉起电子发票列表"),

    #         ("startRecord", "开始录音接口"),
    #         ("stopRecord", "停止录音接口"),
    #         ("onVoiceRecordEnd", "监听录音自动停止接口"),
    #         ("playVoice", "播放语音接口"),
    #         ("pauseVoice", "暂停播放接口"),
    #         ("stopVoice", "停止播放接口"),
    #         ("onVoicePlayEnd", "听语音播放完毕接口"),
    #         ("uploadVoice", "上传语音接口"),
    #         ("downloadVoice", "下载语音接口"),
    #         ("translateVoice", "音转文字接口"),
    #     ],
    #     string="JS API Inertface",

    #     config_parameter="wxwork.js_api_list",
    # )

    ticket_interval_time = fields.Integer(
        "Pull interval time", related="company_id.ticket_interval_time", readonly=False
    )

    ticket_interval_type = fields.Selection(
        related="company_id.ticket_interval_type",
        readonly=False,
    )

    get_ticket_last_time = fields.Datetime(
        related="company_id.get_ticket_last_time",
        readonly=False,
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ir_config = self.env["ir.config_parameter"].sudo()

        jsapi_debug = (
            True if ir_config.get_param("wxwork.jsapi_debug") == "True" else False
        )

        res.update(
            jsapi_debug=jsapi_debug,
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ir_config = self.env["ir.config_parameter"].sudo()
        ir_config.set_param("wxwork.jsapi_debug", self.jsapi_debug or "False")

    def update_cron_ticket_interval_time(self):
        try:
            cron = (
                self.env["ir.model.data"]
                .sudo()
                .get_object("wxwork_jsapi", "ir_cron_pull_wxwork_ticket")
            )
            cron.write(
                {
                    "ticket_interval_time": self.ticket_interval_time,
                    "ticket_interval_type": self.ticket_interval_type,
                }
            )
        except ValueError:
            return False

    def get_jsapi_ticket(self):
        """
        获取企业和应用 jsapi ticket
        """
        ir_config = self.env["ir.config_parameter"].sudo()
        debug = ir_config.get_param("wxwork.jsapi_debug")
        if debug:
            _logger.info(
                _("Start to pull enterprise WeChat Ticket of %s") % self.company_id.name
            )
        if self.company_id.corpid == False:
            raise UserError(_("Please fill in correctly Enterprise ID."))
        elif self.company_id.auth_secret == False:
            raise UserError(_("Please fill in the application 'secret' correctly."))
        else:
            if not self.get_ticket_last_time:
                self.get_corp_ticket(self.company_id)
                self.get_agent_ticket(self.company_id)
            else:
                self.compare_wxwork_ticket_time(
                    self.ticket_interval_time,
                    self.ticket_interval_type,
                    self.company_id,
                )
        if debug:
            _logger.info(_("End of pulling enterprise WeChat Ticket"))

    def compare_wxwork_ticket_time(self, company):
        overdue = False
        if company.ticket_interval_type:
            if company.ticket_interval_type == "hours":
                overdue = self.env["wecom.tools"].cheeck_hours_overdue(
                    company.get_ticket_last_time, company.ticket_interval_time
                )
            elif company.ticket_interval_type == "minutes":
                overdue = self.env["wecom.tools"].cheeck_minutes_overdue(
                    company.get_ticket_last_time, company.ticket_interval_time
                )

        if overdue:
            # 超时
            self.get_corp_ticket(company)
            self.get_agent_ticket(company)

    def get_corp_ticket(self, company):
        """
        拉取 企业 jsapi ticket
        """
        ir_config = self.env["ir.config_parameter"].sudo()
        debug = ir_config.get_param("wxwork.jsapi_debug")
        if debug:
            _logger.info(
                _("Start to pull enterprise WeChat of %s : Enterprise ticket")
                % company.name
            )
        wxapi = CorpApi(company.corpid, company.auth_secret)

        try:
            response = wxapi.httpCall(
                CORP_API_TYPE["GET_JSAPI_TICKET"],
                {
                    "access_token": wxapi.getAccessToken(),
                },
            )
            if company.corp_jsapi_ticket != response["ticket"]:
                # self.company_id.corp_jsapi_ticket = response["ticket"]
                company.write(
                    {
                        "corp_jsapi_ticket": response["ticket"],
                    }
                )

            if debug:
                _logger.info(
                    _(
                        "Finish pulling enterprise WeChat Ticket of %s: Enterprise ticket"
                    )
                    % company.name
                )
        except ApiException as ex:
            if debug:
                _logger.warning(
                    _(
                        "Failed to pull enterprise WeChat Ticket of %s: Enterprise ticket, Error code:%s, Error info:%s"
                    )
                    % (
                        company.name,
                        str(ex.errCode),
                        Errcode.getErrcode(ex.errCode),
                        ex.errMsg,
                    )
                )
            raise UserError(
                _("Error code: %s \nError description: %s \nError Details:\n%s")
                % (str(ex.errCode), Errcode.getErrcode(ex.errCode), ex.errMsg)
            )

    def get_agent_ticket(self, company):
        """
        拉取 应用 jsapi ticket
        """
        ir_config = self.env["ir.config_parameter"].sudo()
        debug = ir_config.get_param("wxwork.jsapi_debug")
        if debug:
            _logger.info(
                _("Start to pull enterprise WeChat Ticket of %s: Application ticket")
                % company.name
            )
        wxapi = CorpApi(company.corpid, company.auth_secret)
        try:
            response = wxapi.httpCall(
                CORP_API_TYPE["GET_TICKET"],
                {
                    "access_token": wxapi.getAccessToken(),
                    "type": "agent_config",
                },
            )
            if self.company_id.agent_jsapi_ticket != response["ticket"]:
                company.write(
                    {
                        "agent_jsapi_ticket": response["ticket"],
                        "get_ticket_last_time": datetime.datetime.now(),
                    }
                )
                # self.company_id.agent_jsapi_ticket = response["ticket"]
                # self.company_id.get_ticket_last_time = datetime.datetime.now()

            if debug:
                _logger.info(
                    _(
                        "Finish pulling enterprise WeChat Ticket of %s: Application ticket"
                    )
                    % company.name
                )
        except ApiException as ex:
            if debug:
                _logger.warning(
                    _(
                        "Failed to pull enterprise WeChat Ticket of %s: Application ticket, Error code:%s, Error info:%s"
                    )
                    % (
                        company.name,
                        str(ex.errCode),
                        Errcode.getErrcode(ex.errCode),
                        ex.errMsg,
                    )
                )
            raise UserError(
                _("Error code: %s \nError description: %s \nError Details:\n%s")
                % (str(ex.errCode), Errcode.getErrcode(ex.errCode), ex.errMsg)
            )

    def get_agent_jsapi_ticket(self):
        ir_config = self.env["ir.config_parameter"].sudo()
        corpid = ir_config.get_param("wxwork.corpid")
        auth_secret = ir_config.get_param("wxwork.auth_secret")
        if corpid == False:
            raise UserError(_("Please fill in correctly Enterprise ID."))
        elif auth_secret == False:
            raise UserError(_("Please fill in the application 'secret' correctly."))

        else:
            wxapi = CorpApi(corpid, auth_secret)
            try:

                response = wxapi.httpCall(
                    CORP_API_TYPE["GET_TICKET"],
                    {
                        "access_token": api.getAccessToken(),
                        "type": "agent_config",
                    },
                )

                if response["errcode"] == 0:
                    if self.agent_jsapi_ticket != response["ticket"]:
                        ir_config.set_param(
                            "wxwork.agent_jsapi_ticket", response["ticket"]
                        )

                        return {
                            "type": "ir.actions.client",
                            "tag": "dialog",
                            "params": {
                                "title": _("Successful operation"),
                                "$content": _(
                                    "<div>Successfully pull the enterprise WeChat application ticket regularly.</div>"
                                ),
                                "size": "medium",
                                "reload": "true",
                            },
                        }

                    else:
                        return {
                            "type": "ir.actions.client",
                            "tag": "dialog",
                            "params": {
                                "title": _("Successful operation"),
                                "$content": _(
                                    "<div>The enterprise WeChat application ticket is within the validity period and does not need to be pulled.</div>"
                                ),
                                "size": "medium",
                            },
                        }
            except ApiException as ex:
                raise UserError(
                    _("Error code: %s \nError description: %s \nError Details:\n%s")
                    % (str(ex.errCode), Errcode.getErrcode(ex.errCode), ex.errMsg)
                )

    def cron_pull_ticket(self):
        companies = (
            self.sudo()
            .env["res.company"]
            .search([(("is_wxwork_organization", "=", True))])
        )
        if len(companies) > 0:
            for company in companies:
                # 遍历companies
                if not company.get_ticket_last_time:
                    self.get_corp_ticket(company)
                    self.get_agent_ticket(company)
                else:
                    self.compare_wxwork_ticket_time(company)

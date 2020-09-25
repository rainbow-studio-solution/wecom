# -*- coding: utf-8 -*-

from odoo import api, fields, models

from odoo.addons.auth_signup.models.res_partner import SignupError, now
from odoo.tools import cache
from ...wxwork_api.CorpApi import *


class Users(models.Model):
    _inherit = "res.users"

    def action_reset_password_by_enterprise_wechat(self):
        """
        为每个用户创建注册令牌，并通过企业微信消息推送发送其注册网址
        """
        params = self.env["ir.config_parameter"].sudo()
        corpid = params.get_param("wxwork.corpid")
        agentid = params.get_param("wxwork.message_agentid")
        corpsecret = params.get_param("wxwork.message_secret")
        api = CorpApi(corpid, corpsecret)

        # 准备重置密码注册
        create_mode = bool(self.env.context.get("create_user"))

        # 初次邀请没有时间限制，仅重设密码
        expiration = False if create_mode else now(days=+1)

        self.mapped("partner_id").signup_prepare(
            signup_type="reset", expiration=expiration
        )

        # 获取 '密码重置'的企业微信消息模板
        message_template = (
            self.sudo()
            .env["wxwork.message.template"]
            .search(
                [("name", "=", "Auth Signup: Reset Password")],
                limit=1,
            )
        )
        message_template_values = {
            "message_to": "${object.wxwork_id|safe}",
            "message_cc": False,
            "auto_delete": True,
            "partner_to": False,
            "scheduled_date": False,
        }
        message_template.write(message_template_values)

        message = {
            # "touser": "${object.wxwork_id|safe}",
            "touser": "rain.wen",
            "msgtype": "markdown",
            "agentid": agentid,
            "markdown": {
                "content": message_template.body_html,
            },
            "enable_duplicate_check": 0,
            "duplicate_check_interval": 1800,
        }

        try:
            response = api.httpCall(
                CORP_API_TYPE["MESSAGE_SEND"],
                {
                    "touser": "rain.wen",
                    "msgtype": "markdown",
                    "agentid": agentid,
                    "markdown": {
                        "content": message_template.body_html,
                    },
                    "enable_duplicate_check": 0,
                    "duplicate_check_interval": 1800,
                },
            )
            print(response)
        except:
            pass

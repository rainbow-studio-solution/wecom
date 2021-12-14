# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from types import CodeType
from odoo import _, api, fields, models


class WeComAppCallbackService(models.Model):
    """
    接收事件服务器配置
    https://work.weixin.qq.com/api/doc/90000/90135/90930
    """

    _name = "wecom.app_callback_service"
    _description = "Wecom Application receive event service"

    app_id = fields.Many2one(
        "wecom.apps",
        string="Application",
        copy=False,
        ondelete="cascade",
        default=lambda self: self.env["wecom.apps"].id,
        # domain="[('company_id', '=', company_id)]",
        required=True,
    )

    def _default_callback_url(self):
        """
        默认回调地址
        :return:"""
        params = self.env["ir.config_parameter"].sudo()
        base_url = params.get_param("web.base.url")
        if self.company_id and self.code:
            return base_url + "/wecom_callback/%s/%s" % (
                self.app_id.code,
                self.app_id.company_id.id,
            )
        else:
            return ""

    name = fields.Char(string="Service Name", required=True)
    code = fields.Char(string="Service Code", copy=False, required=True,)
    callback_url = fields.Char(
        string="URL",
        store=True,
        readonly=True,
        default=_default_callback_url,
        copy=False,
    )  # 回调服务地址
    callback_url_token = fields.Char(string="Token", copy=False)  # Token用于计算签名
    callback_aeskey = fields.Char(string="AES Key", copy=False)  # 用于消息内容加密

    @api.onchange("app_id")
    def _onchange_callback_url(self):
        """
        当应用发生变化时，更新回调服务地址
        :return:
        """
        params = self.env["ir.config_parameter"].sudo()
        base_url = params.get_param("web.base.url")

        if self.app_id:
            self.callback_url = base_url + "/wecom_callback/%s/%s" % (
                self.app_id.code,
                self.app_id.company_id.id,
            )
        else:
            self.callback_url = ""

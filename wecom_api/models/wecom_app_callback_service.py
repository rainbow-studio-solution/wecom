# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from odoo import _, api, fields, models
from odoo.tools.translate import translate
from odoo.exceptions import ValidationError


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

    name = fields.Char(string="Service Name", required=True, translate=True)
    code = fields.Char(string="Service Code", copy=False, required=True,)

    callback_url = fields.Char(
        string="URL",
        store=True,
        readonly=True,
        compute="_default_callback_url",
        copy=False,
    )  # 回调服务地址
    callback_url_token = fields.Char(string="Token", copy=False)  # Token用于计算签名
    callback_aeskey = fields.Char(string="AES Key", copy=False)  # 用于消息内容加密

    description = fields.Text(string="Description", translate=True, copy=True)

    _sql_constraints = [
        (
            "app_code_uniq",
            "unique (app_id,code)",
            _("The code of each application must be unique !"),
        )
    ]

    @api.depends("app_id", "code")
    def _default_callback_url(self):
        """
        默认回调地址
        :return:"""
        params = self.env["ir.config_parameter"].sudo()
        base_url = params.get_param("web.base.url")
        callback_url = ""
        for server in self:
            if self.app_id.company_id and self.code:
                callback_url = base_url + "/wecom_callback/%s/%s" % (
                    self.app_id.company_id.id,
                    self.code,
                )

            server.callback_url = callback_url

    @api.onchange("app_id", "code")
    def _onchange_callback_url(self):
        """
        当应用发生变化时，更新回调服务地址
        :return:
        """
        params = self.env["ir.config_parameter"].sudo()
        base_url = params.get_param("web.base.url")

        if self.app_id:
            self.callback_url = base_url + "/wecom_callback/%s/%s" % (
                self.app_id.company_id.id,
                self.code,
            )
        else:
            self.callback_url = ""

    def generate_service(self):
        """
        生成服务
        :return:
        """
        params = self.env["ir.config_parameter"].sudo()
        base_url = params.get_param("web.base.url")
        if not self.app_id:
            raise ValidationError(_("Please bind contact app!"))
        else:
            self.callback_url = base_url + "/wecom_callback/%s/%s" % (
                self.app_id.company_id.id,
                self.code,
            )

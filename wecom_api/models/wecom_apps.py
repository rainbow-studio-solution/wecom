# -*- coding: utf-8 -*-

from odoo import fields, models, _


class WeComApps(models.Model):
    _inherit = "wecom.apps"

    # 访问令牌
    access_token = fields.Char(string="Access Token", readonly=True)
    expiration_time = fields.Datetime(string="Expiration Time", readonly=True)

    # 接收事件服务器配置
    # https://work.weixin.qq.com/api/doc/90000/90135/90930

    callback_url = fields.Char(string="Callback URL")  # 回调服务地址
    callback_url_token = fields.Char(string="Callback URL Token")  # Token用于计算签名
    callback_aeskey = fields.Char(string="Callback AES Key")  # 用于消息内容加密

    def get_app_info(self):
        """
        获取企业应用信息
        :param agentid:
        :return:
        """

    def set_app_info(self):
        """
        设置企业应用信息
        :param agentid:
        :return:
        """

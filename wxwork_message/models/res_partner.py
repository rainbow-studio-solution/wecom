# -*- coding: utf-8 -*-


from odoo import models


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = ["res.partner", "mail.thread.wxwork_id"]

    def _wxwork_message_get_default_partners(self):
        """ 
        重写mail.thread方法。
        合作伙伴上的企业微信用户是合作伙伴本身。 
        """
        return self

    def _wxwork_message_get_userid_fields(self):
        """ 
        This method returns the fields to use to find the number to use to
        send an SMS on a record.
        此方法返回用于查找记录上发送企业微信消息的企业微信用户ID的字段。
         """
        return ["wxwork_id"]


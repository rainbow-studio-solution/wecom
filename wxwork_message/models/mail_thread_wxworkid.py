# -*- coding: utf-8 -*-

from odoo import models


class WxWorkUserIdMixin(models.AbstractModel):
    _inherit = "mail.thread.wxworkid"

    def _wxworkid_get_userid_fields(self):
        """ 
        添加来自企业微信消息实施的字段
        """
        wxwork_message_fields = self._wxwork_message_get_userid_fields()
        res = super(WxWorkUserIdMixin, self)._wxworkid_get_userid_fields()
        for fname in (f for f in res if f not in wxwork_message_fields):
            wxwork_message_fields.append(fname)
        return wxwork_message_fields

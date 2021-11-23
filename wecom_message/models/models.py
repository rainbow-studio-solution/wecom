# -*- coding: utf-8 -*-

from lxml.builder import E

from odoo import api, models, tools, _


class BaseModel(models.AbstractModel):
    _inherit = "base"

    def _wecom_message_get_default_recipients(self):
        """Generic implementation for finding default recipient to mail on
        a recordset. This method is a generic implementation available for
        all models as we could send an email through mail templates on models
        not inheriting from mail.thread.

        Override this method on a specific model to implement model-specific
        behavior. Also consider inheriting from ``mail.thread``."""
        res = {}
        for record in self:
            # :TODO
            message_to_user = []
            message_to_party = []
            message_to_tag = []

            if "wecom_user_id" in record and record.wecom_user_id:
                message_to_user.append(record.wecom_user_id)
            res[record.id] = {
                "message_to_user": message_to_user,
                "message_to_party": "",
                "message_to_tag": "",
            }
        return res

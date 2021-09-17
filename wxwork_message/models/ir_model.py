# -*- coding: utf-8 -*-


from odoo import api, fields, models


class IrModel(models.Model):
    _inherit = "ir.model"

    is_mail_thread_wxwork_message = fields.Boolean(
        string="Mail Thread Enterprise WeChat Message",
        default=False,
        store=False,
        compute="_compute_is_mail_thread_wxwork_message",
        search="_search_is_mail_thread_wxwork_message",
        help="Does it support sending messages and notifications through enterprise wechat",
    )

    @api.depends("is_mail_thread")
    def _compute_is_mail_thread_wxwork_message(self):
        for model in self:
            if model.is_mail_thread:
                ModelObject = self.env[model.model]
                potential_fields = (
                    ModelObject._wxwork_message_get_userid_fields()
                    + ModelObject._wxwork_message_get_partner_fields()
                )
                if any(fname in ModelObject._fields for fname in potential_fields):
                    model.is_mail_thread_wxwork_message = True
                    continue
            model.is_mail_thread_wxwork_message = False

    def _search_is_mail_thread_wxwork_message(self, operator, value):
        thread_models = self.search([("is_mail_thread", "=", True)])
        valid_models = self.env["ir.model"]
        for model in thread_models:
            if model.model not in self.env:
                continue
            ModelObject = self.env[model.model]
            potential_fields = (
                ModelObject._wxwork_message_get_userid_fields()
                + ModelObject._wxwork_message_get_partner_fields()
            )
            if any(fname in ModelObject._fields for fname in potential_fields):
                valid_models |= model

        search_sms = (operator == "=" and value) or (operator == "!=" and not value)
        if search_sms:
            return [("id", "in", valid_models.ids)]
        return [("id", "not in", valid_models.ids)]


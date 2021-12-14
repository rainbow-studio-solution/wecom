# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError

from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )

    def get_contacts_access_token(self):
        params = {}
        try:
            wxapi = self.env["wecom.service_api"].InitServiceApi(
                self.company_id, "contacts_secret", "contacts"
            )

            if self.company_id.contacts_access_token is False:
                self.company_id.contacts_access_token = wxapi.access_token
            elif wxapi.expiration_time > datetime.now():
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": _("Tips"),
                        "type": "info",
                        "message": _(
                            "Token is still valid, and no update is required!"
                        ),
                        "sticky": False,
                    },
                }
            else:
                self.company_id.contacts_access_token = wxapi.access_token
        except ApiException as ex:
            return self.env["wecom.tools"].ApiExceptionDialog(ex)

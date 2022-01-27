# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException
import logging

_logger = logging.getLogger(__name__)


class WxworkContactsBlock(models.Model):
    _name = "wecom.contacts.block"
    _description = "Wecom contacts synchronization block list"

    name = fields.Char(
        string="Name", readonly=True, copy=False, compute="_compute_name", store=True,
    )  # required=True,readonly=True, store=True
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        domain="[('is_wecom_organization', '=', True)]",
        copy=False,
        required=True,
    )

    wecom_userid = fields.Char(string="WeCom user Id", required=True)

    _sql_constraints = [
        (
            "userid_company_uniq",
            "unique (wecom_userid, company_id)",
            "The user ID of each company must be unique!",
        ),
    ]

    @api.depends("company_id", "wecom_userid")
    def _compute_name(self):
        for block in self:
            if block.company_id and block.wecom_userid:
                company = block.company_id
                name = ""
                try:
                    wxapi = self.env["wecom.service_api"].InitServiceApi(
                        company.corpid, company.contacts_app_id.secret
                    )
                    response = wxapi.httpCall(
                        self.env["wecom.service_api_list"].get_server_api_call(
                            "USER_GET"
                        ),
                        {"userid": block.wecom_userid},
                    )
                    name = response["name"]
                except ApiException as ex:
                    return self.env["wecomapi.tools.action"].ApiExceptionDialog(
                        ex, raise_exception=True
                    )
                finally:
                    block.name = name

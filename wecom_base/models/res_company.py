# -*- coding: utf-8 -*-


import io
import logging
import os

from odoo import api, fields, models, tools, _
from odoo.tools.translate import translate


class Company(models.Model):
    _inherit = "res.company"

    # 基础
    abbreviated_name = fields.Char("Abbreviated Name", translate=True)
    is_wecom_organization = fields.Boolean("WeCom organization", default=False)
    corpid = fields.Char("Corp ID", default="xxxxxxxxxxxxxxxxxx")

    # 通讯录
    contacts_app_id = fields.Many2one(
        "wecom.apps",
        string="Application",
        # required=True,
        # default=lambda self: self.env.company,
        domain="[('company_id', '=', current_company_id)]",
    )
    contacts_secret = fields.Char(
        "Contact Secret", default="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    )
    contacts_access_token = fields.Char(string="Contact token", readonly=True,)

    # contacts_auto_sync_hr_enabled = fields.Boolean(
    #     "Allow WeCom Contacts are automatically updated to HR", default=True,
    # )
    # contacts_sync_hr_department_id = fields.Integer(
    #     "WeCom department ID to be synchronized", default=1,
    # )
    # contacts_edit_enabled = fields.Boolean(
    #     "Allow API to edit WeCom contacts",
    #     default=False,
    #     # readonly=True,
    # )
    # contacts_sync_user_enabled = fields.Boolean(
    #     "Allow WeCom contacts to automatically update system accounts", default=False,
    # )
    # contacts_use_system_default_avatar = fields.Boolean(
    #     "Use system default Avatar", default=True,
    # )
    # contacts_update_avatar_every_time_sync = fields.Boolean(
    #     "Update avatar every time sync", default=False,
    # )

    # corp_jsapi_ticket = fields.Char("Enterprise JS API Ticket",)

    # agent_jsapi_ticket = fields.Char("Application JS API Ticket",)

    # js_api_list = fields.Char("JS API Inertface List")

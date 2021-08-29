# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class Company(models.Model):
    _inherit = "res.company"

    message_agentid = fields.Char("Message Agent Id", default="0000000",)

    message_secret = fields.Char(
        "Message Secret", default="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    )

    module_gamification = fields.Boolean("",)
    module_wxwork_hr_gamification_message = fields.Boolean(
        "Send messages to motivate users via Enterprise WeChat",
    )

    module_digest = fields.Boolean("KPI Digests",)
    module_wxowrk_digest_message = fields.Boolean(
        "Send KPI Digests periodically via Enterprise WeChat",
    )

    module_stock = fields.Boolean("",)
    module_wxwork_stock_message = fields.Boolean(
        "Send Inventory message via Enterprise WeChat",
    )

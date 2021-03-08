# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    message_agentid = fields.Char(
        "Agent Id", config_parameter="wxwork.message_agentid", default="0000000",
    )
    message_secret = fields.Char(
        "Secret",
        config_parameter="wxwork.message_secret",
        default="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    )

    module_gamification = fields.Boolean("",)
    module_wxwork_hr_gamification_message = fields.Boolean(
        "Send messages to motivate users via Enterprise WeChat",
    )

    module_digest = fields.Boolean("",)
    module_wxowrk_digest_message = fields.Boolean(
        "Send KPI Digests periodically via Enterprise WeChat",
    )

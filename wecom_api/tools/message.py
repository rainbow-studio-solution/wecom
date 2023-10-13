# -*- coding: utf-8 -*-

from odoo import api, models, tools, _
import logging

_logger = logging.getLogger(__name__)


class WecomApiToolsMessage(models.AbstractModel):
    _name = "wecomapi.tools.message"
    _description = "Wecom API Tools - Message"

    def message_split(self,text):
        """ """

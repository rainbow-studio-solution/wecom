# -*- coding: utf-8 -*-

import base64
import logging
from lxml import etree, html
from html.parser import HTMLParser
import lxml.html
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class WxWorkMessageTemplate(models.Model):
    "Template for sending Enterprise WeChat message"
    # _name = "wxwork.message.template"
    _inherit = ["mail.template"]
    # _inherit = ["mail.render.mixin"]
    _description = "Enterprise WeChat Message Templates"
    _order = "name"


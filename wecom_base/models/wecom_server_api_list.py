# -*- coding: utf-8 -*-

import re
from odoo import api, fields, models, SUPERUSER_ID, _


class WecomServerApiList(models.Model):
    _inherit = "wecom.service_api_list"
    
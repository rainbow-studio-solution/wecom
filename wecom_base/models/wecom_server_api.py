# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from odoo import api, fields, models, SUPERUSER_ID, _

class WecomServerApi(models.TransientModel):
    _inherit = "wecom.service_api"
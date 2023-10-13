# -*- coding: utf-8 -*-


import requests
import logging
from urllib.parse import quote, unquote
import pandas as pd

pd.set_option("max_colwidth", 4096)

from lxml import etree
import requests
from odoo import api, fields, models, SUPERUSER_ID, _

_logger = logging.getLogger(__name__)


class WecomServerApiError(models.Model):
    _inherit = "wecom.service_api_error"
    

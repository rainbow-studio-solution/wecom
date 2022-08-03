# -*- coding: utf-8 -*-

import logging
import datetime
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

from io import StringIO
import pandas as pd

pd.set_option("max_colwidth", 4096)  # 设置最大列宽
pd.set_option("display.max_columns", 30)  # 设置最大列数
pd.set_option("expand_frame_repr", False)  # 当列太多时不换行
import time

from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException

_logger = logging.getLogger(__name__)


class WeComApps(models.Model):
    _inherit = "wecom.apps"

    def get_checkin_rules(self):
        """
        获取打卡规则
        """
        result = {}

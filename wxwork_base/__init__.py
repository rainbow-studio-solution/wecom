# -*- coding: utf-8 -*-

from . import controllers
from . import models


from odoo import api, SUPERUSER_ID


def _open_wxwork_settings(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["res.config.settings"].open_wxwork_settings()


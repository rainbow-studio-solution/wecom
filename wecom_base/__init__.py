# -*- coding: utf-8 -*-

from . import controllers
from . import models


from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['ir.http'].clear_caches()
    env['ir.ui.view'].clear_caches()

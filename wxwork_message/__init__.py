# -*- coding: utf-8 -*-

from . import models
from . import wizard
from . import controllers

from odoo import api, SUPERUSER_ID


# def _auto_install_lang(cr, registry):
#     """
#     安装英语
#     """
#     env = api.Environment(cr, SUPERUSER_ID, {})

#     language = (
#         env["res.lang"]
#         .with_context(active_test=False)
#         .search([("code", "=", "en_US")], limit=1)
#     )

#     if language:
#         language.write({"active": True})
#         return language.id

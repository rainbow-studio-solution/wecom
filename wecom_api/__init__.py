# -*- coding: utf-8 -*-

from odoo.tools import sql
from . import api
from . import tools
from . import models
from . import controllers


# from odoo import api, SUPERUSER_ID, _


# def post_init_hook(cr, registry):
#     # 安装模块后清理 清除所有的记录，并且索引号从0开始
#     env = api.Environment(cr, SUPERUSER_ID, {})
#     query = """
#     TRUNCATE TABLE wecom_app_config RESTART IDENTITY CASCADE;
#     """
#     env.cr.execute(query)

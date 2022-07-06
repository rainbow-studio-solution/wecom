# -*- coding: utf-8 -*-

from . import models
from . import controllers
from . import wizard



# import logging
# import shutil, platform, os, os.path
# from odoo import api, SUPERUSER_ID, _
# from odoo.exceptions import UserError
# from odoo.modules import get_module_path

# _logger = logging.getLogger(__name__)


# def pre_init_hook(cr):
#     env = api.Environment(cr, SUPERUSER_ID, {})
#     path = env["ir.config_parameter"].get_param("wecom.resources_path")

#     if platform.system() == "Windows":
#         destination = path.replace("\\", "/") + "sdk/"
#     else:
#         destination = path + "sdk/"

#     module_path = get_module_path("wecom_msgaudit")
#     source = env["wecomapi.tools.file"].path_is_exists(module_path, "/sdk")

#     if path:
#         try:
#             shutil.copytree(source, destination)
#             # shutil.copytree(源文件，指定路径)
#             # copytree不能把文件夹复制到已存在的文件夹里面去。
#         except BaseException as e:
#             _logger.info(
#                 _("Unable to create session archive SDK folder! Error:%s") % (repr(e))
#             )

#     else:
#         # 尚未配置路径
#         raise UserError(_("WeCom resources storage path has not been configured yet!"))

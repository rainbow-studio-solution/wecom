# -*- coding: utf-8 -*-

from . import models


import os.path
from odoo import api, SUPERUSER_ID, _
from odoo.exceptions import UserError


def pre_init_hook(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    path = env["ir.config_parameter"].get_param("wxwork.img_path")

    if path:
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except BaseException as e:
                raise UserError(
                    _("Unable to create enterprise wechat image storage path! Error:%s")
                    % (repr(e))
                )
    else:
        raise UserError(
            _("Enterprise WeChat image storage path has not been configured yet!")
        )


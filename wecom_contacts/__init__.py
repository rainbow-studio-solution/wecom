# -*- coding: utf-8 -*-


# from . import controllers
from . import models

# from . import wizard
from odoo import api, SUPERUSER_ID, _
from odoo.exceptions import UserError

def pre_init_hook(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    company = env.company
    print(company)
    if not company.corpid:
        raise UserError(
                    _("The current company does not have an Corp ID configured for enterprise wechat")
                )
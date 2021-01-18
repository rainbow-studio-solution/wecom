# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.addons.auth_signup.models.res_partner import SignupError, now
from odoo.tools import cache
from ...wxwork_api.wx_qy_api.CorpApi import *

# from ...wxwork_api.wx_api.corp_api import *


class ResUsers(models.Model):
    _inherit = "res.users"


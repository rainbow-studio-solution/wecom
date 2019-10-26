# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import platform
if (platform.system() == 'Windows'):
    from wxwork.wxwork_api.wxworkapi.CorpApi import CorpApi
else:
    pass


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    attendance_secret = fields.Char("打卡凭证密钥", config_parameter='wxwork.attendance_secret')
    attendance_access_token= fields.Char("打卡token", config_parameter='wxwork.attendance_access_token', readonly=True,)

    def get_attendance_access_token(self):
        if self.corpid == False:
            raise UserError(_("请正确填写企业ID."))
        elif self.contacts_secret == False:
            raise UserError(_("请正确填写打卡凭证密钥."))
        else:
            wxapi = CorpApi(self.corpid, self.attendance_secret)
            self.env['ir.config_parameter'].sudo().set_param(
                "wxwork.attendance_access_token", wxapi.getAccessToken())
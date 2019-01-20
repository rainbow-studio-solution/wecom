# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning
import odoo.addons.decimal_precision as dp


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    dingtalk_app_id=fields.Char(u'钉钉appid')
    dingtalk_qr_appSecret=fields.Char(u'钉钉扫码appSecret')
    dingtalk_corpid = fields.Char(u'钉钉应用corpid')
    dingtalk_corpSecret=fields.Char(u'钉钉应用corpSecret')

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        params = self.env['ir.config_parameter'].sudo()
        params.set_param('dingtalk.appid', self[0].dingtalk_app_id)
        params.set_param('dingtalk.qr.appsecret',self[0].dingtalk_qr_appSecret)
        params.set_param('dingtalk.corpid', self[0].dingtalk_corpid)
        params.set_param('dingtalk.corpSecret', self[0].dingtalk_corpSecret)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            dingtalk_app_id=params.get_param('dingtalk.appid', default=''),
            dingtalk_qr_appSecret=params.get_param('dingtalk.qr.appsecret', default=''),
            dingtalk_corpSecret=params.get_param('dingtalk.corpSecret', default=''),
            dingtalk_corpid=params.get_param('dingtalk.corpid',default='')
        )
        return res

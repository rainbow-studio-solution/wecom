# -*- coding: utf-8 -*-

from odoo import _, api, fields, models, tools

class NoticeTemplate(models.Model):
    _name = 'wxwork_notice.template'
    _description = '企业微信通知模板'
# -*- coding: utf-8 -*-

from ..api.CorpApi import *
from ..helper.common import *
from odoo import api, fields, models

class Users(models.Model):
    _inherit = 'res.users'
    _description = '企业微信员工'
    _order = 'wxwork_user_order'

    userid = fields.Char(string='企微用户Id', readonly=True)
    is_wxwork_notice =fields.Boolean('是否接收提醒', default=True)
    is_wxwork_user = fields.Boolean('企微用户', readonly=True)
    qr_code = fields.Binary(string='个人二维码', help='员工个人二维码，扫描可添加为外部联系人', readonly=True)
    wxwork_user_order = fields.Char(
        '企微用户排序',
        default='0',
        help='部门内的排序值，默认为0。数量必须和department一致，数值越大排序越前面。值范围是[0, 2^32)',
        readonly=True,
    )


    @api.multi
    def sync(self):
        params = self.env['ir.config_parameter'].sudo()
        corpid = params.get_param('wxwork.corpid')
        secret = params.get_param('wxwork.contacts_secret')
        sync_department_id = params.get_param('wxwork.contacts_sync_hr_department_id')

        api = CorpApi(corpid, secret)
        json = api.httpCall(
            CORP_API_TYPE['USER_LIST'],
            {
                'department_id': sync_department_id,
                'fetch_child': '1',
            }
        )
        for obj in json['userlist']:
            records = self.search([
                ('userid', '=', obj['userid']),
                ('is_wxwork_user', '=', True)],
                limit=1)
            if len(records) > 0:
                self.update(obj)
            else:
                self.create(obj)

        # self.set_employee_active(json)

    @api.model
    def create(self,values):
        lines = super(Users, self).create({
            'name': values['name'],
            'login': values['userid'],
            # "email": values['email'],
            # 'userid': values['userid'],
            # 'image': Common(values['avatar']).avatar2image(),
            # 'qr_code': Common(values['qr_code']).avatar2image(),
            # 'active': values['enable'],
            # 'wxwork_user_order': values['order'],
            'is_wxwork_user': True,
        })
        print(lines.name)
        return lines

    @api.model
    def update(self,values):
        super(Users, self).write({
            'name': values['name'],
            'active': values['enable'],
            "email": values['email'],
            'wxwork_user_order': values['order'],
            'is_wxwork_user': True,
        })

    @api.multi
    def wxwork_message_send(self):
        pass





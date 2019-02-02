# -*- coding: utf-8 -*-

from odoo import api, fields, models
from ..api.CorpApi import *
from ..helper.common import *
import logging,platform
from threading import Thread, Lock
import time

class Users(models.Model):
    _inherit = 'res.users'
    _description = '企业微信员工'
    _order = 'wxwork_user_order'

    wxwork_id = fields.Char(string='企微用户ID', readonly=True)
    is_wxwork_notice =fields.Boolean('是否接收提醒', default=True)
    is_wxwork_user = fields.Boolean('企微用户', readonly=True)
    # qr_code = fields.Binary(string='个人二维码', help='员工个人二维码，扫描可添加为外部联系人', readonly=True)
    wxwork_user_order = fields.Char(
        '企微用户排序',
        default='0',
        help='部门内的排序值，默认为0。数量必须和department一致，数值越大排序越前面。值范围是[0, 2^32)',
        readonly=True,
    )


    @api.multi
    def sync_user(self):
        params = self.env['ir.config_parameter'].sudo()
        corpid = params.get_param('wxwork.corpid')
        secret = params.get_param('wxwork.contacts_secret')
        sync_department_id = params.get_param('wxwork.contacts_sync_hr_department_id')
        api = CorpApi(corpid, secret)
        lock = Lock()
        start = time.time()
        try:
            response = api.httpCall(
                CORP_API_TYPE['USER_LIST'],
                {
                    'department_id': sync_department_id,
                    'fetch_child': '1',
                }
            )

            for obj in response['userlist']:
                threaded_sync = Thread(target=self.run, args=[obj,lock])
                threaded_sync.start()

            end = time.time()
            times = end - start
            result = "用户同步成功,花费时间 %s 秒" % (round(times,3))
            # status = "user:%s" % True
            status = {'user': True}
        except BaseException as e:
            result = "用户同步失败,花费时间 %s 秒" % (round(times, 3))
            status = {'user': False}
            print('用户同步 错误:%s' % (repr(e)))

        return times, status, result


    @api.multi
    def run(self,obj,lock):
        lock.acquire()
        with api.Environment.manage():
            new_cr = self.pool.cursor()
            self = self.with_env(self.env(cr=new_cr))
            env = self.sudo().env['res.users']
            domain = ['|', ('active', '=', False),
                      ('active', '=', True)]
            user = env.search(
                domain + [
                    ('wxwork_id', '=', obj['userid']),
                    ('is_wxwork_user', '=', True)],
                limit=1)

            try:
                if len(user) > 0:
                    self.update_user(user, obj)
                else:
                    self.create_user(user, obj)

            except Exception as e:
                print('线程同步用户错误:%s' % (repr(e)))
            new_cr.commit()
            new_cr.close()
        lock.release()

    @api.multi
    def create_user(self, user, obj):
        img_path = self.env['ir.config_parameter'].sudo().get_param('wxwork.contacts_img_path')
        if (platform.system() == 'Windows'):
            avatar_file = img_path.replace("\\", "/") + "/avatar/" + obj['userid'] + ".jpg"
        else:
            avatar_file = img_path + "avatar/" + obj['userid'] + ".jpg"

        groups_id = self.sudo().env['res.groups'].search([('id', '=', 9), ], limit=1).id

        try:
            user.create({
                'name': obj['name'],
                'login': obj['userid'],
                'oauth_uid': obj['userid'],
                'password': Common(8).random_passwd(),
                'email': obj['email'],
                'wxwork_id': obj['userid'],
                'image': self.encode_image_as_base64(avatar_file),
                # 'qr_code': employee.qr_code,
                'active':obj['enable'],
                'wxwork_user_order': obj['order'],
                'mobile': obj['mobile'],
                'phone':  obj['telephone'],
                'is_wxwork_user': True,
                'is_moderator': False,
                'is_company': False,
                'supplier': False,
                'employee': True,
                'share': False,
                'groups_id': [(6, 0, [groups_id])],  # 设置用户为门户用户
            })
            result = True
        except Exception as e:
            print('%s创建错误 - %s' % (obj['name'], repr(e)))
            result = False
        return result

    @api.multi
    def update_user(self, user, obj):
        img_path = self.env['ir.config_parameter'].sudo().get_param('wxwork.contacts_img_path')
        if (platform.system() == 'Windows'):
            avatar_file = img_path.replace("\\", "/") + "/avatar/" + obj['userid'] + ".jpg"
        else:
            avatar_file = img_path + "avatar/" + obj['userid'] + ".jpg"
        try:
            user.write({
                'name': obj['name'],
                'oauth_uid': obj['userid'],
                'email': obj['email'],
                'image': self.encode_image_as_base64(avatar_file),
                'wxwork_user_order': obj['order'],
                'is_wxwork_user': True,
                'mobile': obj['mobile'],
                'phone': obj['telephone'],
            })
            result = True
        except Exception as e:
            print('%s更新错误 - %s' % (obj['name'], repr(e)))
            result = False
        return result

    @api.multi
    def encode_image_as_base64(self, image_path):
        if not os.path.exists(image_path):
            pass
        else:
            try:
                with open(image_path, "rb") as f:
                    encoded_string = base64.b64encode(f.read())
                return encoded_string
            except BaseException as e:
                return None

class ChangeTypeWizard(models.TransientModel):
    _name = "change.type.wizard"
    _description = "Change WxWork User Type Wizard"

    def _default_user_ids(self):
        user_ids = self._context.get('active_model') == 'res.users' and self._context.get('active_ids') or []
        return [
            (0, 0, {
                'user_id': user.id,
                'user_login': user.login,
                'user_name': user.name,
            })
            for user in self.env['res.users'].browse(user_ids)
        ]

    user_ids = fields.One2many('change.type.user', 'wizard_id', string='用户', default=_default_user_ids)

    @api.multi
    def change_type_button(self):
        self.ensure_one()
        self.user_ids.change_type_button()
        if self.env.user in self.mapped('user_ids.user_id'):
            return {'type': 'ir.actions.client', 'tag': 'reload'}
        return {'type': 'ir.actions.act_window_close'}

class ChangeTypeUser(models.TransientModel):
    _name = 'change.type.user'
    _description = 'User, Change Type Wizard'

    wizard_id = fields.Many2one('change.type.wizard', string='Wizard', required=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', string='User', required=True, ondelete='cascade')
    user_login = fields.Char(string='登录账号', readonly=True)
    user_name = fields.Char(string='名称', readonly=True)
    choices = (('1', '内部用户'),('9', '门户用户'),('10', '公共用户'))
    new_type = fields.Selection(choices, string='用户类型', default='')

    @api.multi
    def change_type_button(self):
        for line in self:
            if not line.new_type:
                raise UserError("在点击'更改用户类型'按钮之前，您必须修改新的用户类型")
            if line.user_id.id ==1 or line.user_id.id==2 or line.user_id.id==3 or line.user_id.id==4 or line.user_id.id==5:
                pass
            else:
                line.user_id.write({
                    'groups_id':  [(6, 0, line.new_type)]
                })
        self.write({'new_type': False})

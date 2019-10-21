# -*- coding: utf-8 -*-

from odoo import api, fields, models
from wxworkapi.CorpApi import CorpApi, CORP_API_TYPE

from ..helper.common import *
import logging,platform
import time

_logger = logging.getLogger(__name__)

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _description = '企业微信员工'
    _order = 'wxwork_user_order'

    wxwork_id = fields.Char(string='企微用户Id', readonly=True)
    alias = fields.Char(string='别名', readonly=True)
    department_ids = fields.Many2many('hr.department', string='企微多部门', readonly=True)
    qr_code = fields.Binary(string='个人二维码', help='员工个人二维码，扫描可添加为外部联系人', readonly=True)
    wxwork_user_order = fields.Char(
        '企微用户排序',
        default='0',
        help='部门内的排序值，默认为0。数量必须和department一致，数值越大排序越前面。值范围是[0, 2^32)',
        readonly=True,
    )
    is_wxwork_employee = fields.Boolean('企微员工', readonly=True)

    user_check_tick = fields.Boolean('User Check Tick')

    def create_user_from_employee(self):
        '''
        从员工生成用户
        :return:
        '''
        groups_id = self.sudo().env['res.groups'].search([('id', '=', 9), ], limit=1).id
        res_user_id = self.env['res.users'].create({
            'name': self.name,
                'login': self.wxwork_id,
                'oauth_uid': self.wxwork_id,
                'password': Common(8).random_passwd(),
                'email': self.work_email,
                'wxwork_id': self.wxwork_id,
                'image_1920': self.image_1920,
                # 'qr_code': employee.qr_code,
                'active': self.active,
                'wxwork_user_order': self.wxwork_user_order,
                'mobile': self.mobile_phone,
                'phone': self.work_phone,
                'notification_type': 'wxwork',
                'is_wxwork_user': True,
                'is_moderator': False,
                'is_company': False,
                'employee': True,
                'share': False,
                'groups_id': [(6, 0, [groups_id])],  # 设置用户为门户用户
        })
        self.user_id = res_user_id.id
        self.address_home_id = res_user_id.partner_id.id
        self.user_check_tick = True

    @api.onchange('address_home_id')
    def user_checking(self):
        if self.address_home_id:
            self.user_check_tick = True
        else:
            self.user_check_tick = False

    def sync_employee(self):
        _logger.error("开始同步企业微信通讯录-员工同步")
        params = self.env['ir.config_parameter'].sudo()
        corpid = params.get_param('wxwork.corpid')
        secret = params.get_param('wxwork.contacts_secret')
        sync_department_id = params.get_param('wxwork.contacts_sync_hr_department_id')
        api = CorpApi(corpid, secret)
        # lock = Lock()
        try:
            response = api.httpCall(
                CORP_API_TYPE['USER_LIST'],
                {
                    'department_id': sync_department_id,
                    'fetch_child': '1',
                }
            )
            start1 = time.time()
            for obj in response['userlist']:
                # threaded_sync = Thread(target=self.run_sync, args=[obj,lock])
                # threaded_sync.start()
                self.run_sync(obj)
            end1 = time.time()
            times1 = end1 - start1

            start2 = time.time()
            self.sync_leave_employee(response)
            # threaded_sync_leave = Thread(target=self.sync_leave_employee, args=[response,lock])
            # threaded_sync_leave.start()
            end2 = time.time()
            times2 = end2 - start2

            times = times1 + times2
            status = {'employee': True}
            result = "员工同步成功,花费时间 %s 秒" % (round(times, 3))
        except BaseException as e:
            result = "员工同步失败,花费时间 %s 秒" % (round(times, 3))
            status = {'employee': False}
            print('员工同步错误:%s' % (repr(e)))

        _logger.error("结束同步企业微信通讯录-员工同步，总共花费时间：%s 秒" % times)
        return times, status, result

    def run_sync(self, obj):
        with api.Environment.manage():
            new_cr = self.pool.cursor()
            self = self.with_env(self.env(cr=new_cr))
            env = self.sudo().env['hr.employee']
            domain = ['|', ('active', '=', False),
                      ('active', '=', True)]
            records = env.search(
                domain + [
                    ('wxwork_id', '=', obj['userid']),
                    ('is_wxwork_employee', '=', True)],
                limit=1)

            try:
                if len(records) > 0:
                    self.update_employee(records, obj)
                else:
                    self.create_employee(records, obj)
            except Exception as e:
                print(repr(e))
            new_cr.commit()
            new_cr.close()

    def create_employee(self,records, obj):
        department_ids = []
        for department in obj['department']:
            department_ids.append(self.get_employee_parent_wxwork_department(department))

        # department_id = []
        # if len(obj['department'])>1:
        #     department_id = None
        # else:
        #     department_id = self.get_employee_parent_hr_department(obj['department'])

        img_path = self.env['ir.config_parameter'].sudo().get_param('wxwork.contacts_img_path')
        if (platform.system() == 'Windows'):
            avatar_file = img_path.replace("\\","/") + "/avatar/" + obj['userid'] + ".jpg"
            qr_code_file = img_path.replace("\\","/")  + "/qr_code/" + obj['userid'] + ".png"
        else:
            avatar_file = img_path + "avatar/" + obj['userid'] + ".jpg"
            qr_code_file = img_path + "qr_code/" + obj['userid'] + ".png"

        try:
            records.create({
                'wxwork_id': obj['userid'],
                'name': obj['name'],
                'gender': Common(obj['gender']).gender(),
                'marital': None, # 不生成婚姻状况
                'image_1920': self.encode_image_as_base64(avatar_file),
                'mobile_phone': obj['mobile'],
                'work_phone': obj['telephone'],
                'work_email': obj['email'],
                'active': obj['enable'],
                'alias': obj['alias'],
                # 'department_id':department_id,
                'department_id': department_ids[0],#归属多个部门的情况下，第一个部门为默认部门
                'department_ids': [(6, 0, department_ids)],
                'wxwork_user_order': obj['order'],
                'qr_code': self.encode_image_as_base64(qr_code_file),
                'is_wxwork_employee': True,
            })
            result = True
        except Exception as e:
            print('创建员工错误：%s - %s' % (obj['name'], repr(e)))
            result = False
        return result

    def update_employee(self,records, obj):
        department_ids = []
        for department in obj['department']:
            department_ids.append(self.get_employee_parent_wxwork_department(department))

        # department_id = []
        # if len(obj['department']) > 1:
        #     department_id = None
        # else:
        #     department_id = self.get_employee_parent_hr_department(obj['department'])

        img_path = self.env['ir.config_parameter'].sudo().get_param('wxwork.contacts_img_path')
        if (platform.system() == 'Windows'):
            avatar_file = img_path.replace("\\","/") + "/avatar/" + obj['userid'] + ".jpg"
            qr_code_file = img_path.replace("\\","/")  + "/qr_code/" + obj['userid'] + ".png"
        else:
            avatar_file = img_path + "avatar/" + obj['userid'] + ".jpg"
            qr_code_file = img_path + "qr_code/" + obj['userid'] + ".png"
        try:
            records.write({
                'name': obj['name'],
                'gender': Common(obj['gender']).gender(),
                # 'image_1920': self.encode_image_as_base64(avatar_file),   # 首次同步后，不再更新头像
                'mobile_phone': obj['mobile'],
                'work_phone': obj['telephone'],
                'work_email': obj['email'],
                'active': obj['enable'],
                'alias': obj['alias'],
                # 'department_id': department_id,
                'department_id': department_ids[0], #归属多个部门的情况下，第一个部门为默认部门
                'department_ids': [(6, 0, department_ids)],
                'wxwork_user_order': obj['order'],
                'qr_code': self.encode_image_as_base64(qr_code_file),
                'is_wxwork_employee': True
            })
            result = True
        except Exception as e:
            print('更新员工错误：%s - %s' % (obj['name'], repr(e)))
            result = False

        return result

    def encode_image_as_base64(self,image_path):
        # if not self.sync_img:
        #     return None
        if not os.path.exists(image_path):
            pass
        else:
            try:
                with open(image_path, "rb") as f:
                    encoded_string = base64.b64encode(f.read())
                return encoded_string
            except BaseException as e:
                return None
                # pass+

    def get_employee_parent_hr_department(self,department_obj):
        '''
        如果企微用户只有一个部门，则设置企业用户的HR部门
        :param department_obj: 部门json
        :return:
            企微用户只有一个部门，返回department_id
            企微用户归属多个部门，返回 None
        '''
        try:
            departments = self.env['hr.department'].search([
                ('wxwork_department_id', 'in', department_obj),
                ('is_wxwork_department', '=', True)],
                limit=1)
            if len(departments) > 0:
                return departments.id
        except BaseException as e:
            print('获取员工上级部门错误:%s' % (repr(e)))


    def get_employee_parent_wxwork_department(self,department_id):
        try:
            departments = self.env['hr.department'].search([
                ('wxwork_department_id', '=', department_id),
                ('is_wxwork_department', '=', True)],
                limit=1)
            if len(departments) > 0:
                return departments.id
        except BaseException as e:
            print('获取员工上级部门错误:%s' % (repr(e)))

    def sync_leave_employee(self,response):
        """比较企业微信和odoo的员工数据，且设置离职odoo员工active状态"""
        try:
            list_user = []
            list_employee = []
            for wxwork_employee in response['userlist']:
                list_user.append(wxwork_employee['userid'])

            with api.Environment.manage():
                new_cr = self.pool.cursor()
                self = self.with_env(self.env(cr=new_cr))
                env = self.sudo().env['hr.employee']
                domain = ['|', ('active', '=', False),
                          ('active', '=', True)]
                employees = env.search(
                    domain + [
                        ('is_wxwork_employee', '=', True)
                    ])
                for employee in employees:
                    list_employee.append(employee.wxwork_id)

                list_user_leave = list(set(list_employee).difference(set(list_user))) #生成odoo与企微不同的员工数据列表
                for wxwork_leave_employee in list_user_leave:
                    leave_employee  = employees.search([
                        ('wxwork_id', '=', wxwork_leave_employee)
                    ])
                    self.set_employee_active(leave_employee )
                    # print(leave_employee.name + str(op))
                new_cr.commit()
                new_cr.close()
        except Exception as e:
            print('生成离职员工数据错误:%s' % (repr(e)))

    def set_employee_active(self,records,lock):
        # lock.acquire()
        try:
            records.write({
                'active': False,
            })
            # return True
        except Exception as e:
            print('离职员工:%s 同步错误:%s' % (records.name,repr(e)))
            # return False
        # lock.release()

class EmployeeBindingUser(models.Model):
    _inherit = 'hr.employee'
    _description = '企业微信员工绑定用户'

    def binding(self):
        _logger.error("开始同步企业微信通讯录-用户绑定")

        domain = ['|', ('active', '=', False),
                  ('active', '=', True)]
        with api.Environment.manage():
            new_cr = self.pool.cursor()
            self = self.with_env(self.env(cr=new_cr))

            employees = self.sudo().env['hr.employee'].search(
                domain+ [
                    ('is_wxwork_employee', '=', True)
                ]
            )

            start = time.time()
            for employee in employees:
                user = self.sudo().env['res.users'].search(
                    domain+ [
                        ('wxwork_id', '=', employee.wxwork_id),
                        ('is_wxwork_user', '=', True)
                    ],limit=1)

                try:
                    # threaded_sync = Thread(target=self.run, args=[user, employee])
                    # threaded_sync.start()
                    if len(user) > 0:
                        self.update_user(user, employee)
                    else:
                        employee.write({
                            'user_id':self.create_user(user, employee).id
                        })
                    # employee.user_id =self.create_user(user, employee).id
                    result = "员工绑定用户成功"
                    status = {'binding': True}
                except Exception as e:
                    result = "员工绑定用户失败"
                    status = {'binding': False}
                    print('从员工绑定用户错误:%s' % (repr(e)))
            end = time.time()
            times = end - start
            new_cr.commit()
            new_cr.close()
            _logger.error("结束同步企业微信通讯录-员工绑定，总共花费时间：%s 秒" % times)
        return times, status, result

    def run(self, user, employee):
        if len(user) > 0:
            self.update_user(user, employee)
        else:
            user_id = self.create_user(user, employee).id
            employee.write({
                'user_id':user_id
            })

    def create_user(self, user, employee):
        try:
            groups_id = self.sudo().env['res.groups'].search([('id', '=', 9), ], limit=1).id
            user_id = user.create({
                'name': employee.name,
                'login': employee.wxwork_id,
                'oauth_uid': employee.wxwork_id,
                'password': Common(8).random_passwd(),
                'email': employee.work_email,
                'wxwork_id': employee.wxwork_id,
                'image_1920': employee.image_1920,
                # 'qr_code': employee.qr_code,
                'active': employee.active,
                'wxwork_user_order': employee.wxwork_user_order,
                'mobile': employee.mobile_phone,
                'phone': employee.work_phone,
                'notification_type': 'wxwork',
                'is_wxwork_user': True,
                'is_moderator': False,
                'is_company': False,
                'supplier': False,
                'employee': True,
                'share': False,
                'groups_id': [(6, 0, [groups_id])],  # 设置用户为门户用户
            })
            return user_id
        except Exception as e:
            print('从员工创建用户错误:%s' % (repr(e)))

    def update_user(self, user, employee):
        try:
            user.write({
                'name': employee.name,
                'oauth_uid': employee.wxwork_id,
                # 'email': employee.work_email,
                'image_1920': employee.image_1920,
                'wxwork_user_order': employee.wxwork_user_order,
                'is_wxwork_user': True,
                'mobile': employee.mobile_phone,
                'phone': employee.work_phone,
            })
        except Exception as e:
            print('从员工更新用户错误:%s' % (repr(e)))

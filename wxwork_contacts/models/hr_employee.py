# -*- coding: utf-8 -*-

from odoo import api, fields, models
from ..api.CorpApi import *
from ..helper.common import *
import logging,platform
from threading import Thread, Lock
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

    @api.multi
    def sync_employee(self):
        params = self.env['ir.config_parameter'].sudo()
        corpid = params.get_param('wxwork.corpid')
        secret = params.get_param('wxwork.contacts_secret')
        sync_department_id = params.get_param('wxwork.contacts_sync_hr_department_id')
        api = CorpApi(corpid, secret)
        lock = Lock()
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
                threaded_sync = Thread(target=self.run_sync, args=[obj,lock])
                threaded_sync.start()
            end1 = time.time()
            times1 = end1 - start1

            time.sleep(5)

            start2 = time.time()
            threaded_sync_leave = Thread(target=self.sync_leave_employee, args=[response,lock])
            threaded_sync_leave.start()
            end2 = time.time()
            times2 = end2 - start2

            times = times1 + times2 +5
            result = True
        except BaseException as e:
            print('员工同步错误:%s' % (repr(e)))
            result = False
        return times,result

    @api.multi
    def run_sync(self, obj,lock):
        lock.acquire()
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
        lock.release()

    @api.multi
    def create_employee(self,records, obj):
        department_ids = []
        for department in obj['department']:
            department_ids.append(self.get_employee_parent_department(department))

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
                'image': self.encode_image_as_base64(avatar_file),
                'mobile_phone': obj['mobile'],
                'work_phone': obj['telephone'],
                'work_email': obj['email'],
                'active': obj['enable'],
                'alias': obj['alias'],
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

    @api.multi
    def update_employee(self,records, obj):
        department_ids = []
        for department in obj['department']:
            department_ids.append(self.get_employee_parent_department(department))
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
                'image': self.encode_image_as_base64(avatar_file),
                'mobile_phone': obj['mobile'],
                'work_phone': obj['telephone'],
                'work_email': obj['email'],
                'active': obj['enable'],
                'alias': obj['alias'],
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

    @api.multi
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
                # pass

    @api.multi
    def get_employee_parent_department(self,department_id):
        try:
            departments = self.env['hr.department'].search([
                ('wxwork_department_id', '=', department_id),
                ('is_wxwork_department', '=', True)],
                limit=1)
            if len(departments) > 0:
                return departments.id
        except BaseException as e:
            print('获取员工上级部门错误:%s' % (repr(e)))

    @api.multi
    def sync_leave_employee(self,response,lock):
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
                    self.set_employee_active(leave_employee ,lock)
                    # print(leave_employee.name + str(op))
                new_cr.commit()
                new_cr.close()
        except Exception as e:
            print('生成离职员工数据错误:%s' % (repr(e)))

    @api.multi
    def set_employee_active(self,records,lock):
        lock.acquire()
        try:
            records.write({
                'active': False,
            })
            # return True
        except Exception as e:
            print('离职员工:%s 同步错误:%s' % (records.name,repr(e)))
            # return False
        lock.release()

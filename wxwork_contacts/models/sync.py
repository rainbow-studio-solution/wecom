# -*- coding: utf-8 -*-

from ..api.CorpApi import *
from ..helper.common import *
import base64,urllib,os
import numpy as np
import cv2


class SyncDepartment(object):
    def __init__(self, corpid, secret, department_id, department):
        self.corpid = corpid
        self.secret = secret
        self.department_id = department_id
        self.department = department
        self.result = None



    def sync_department(self):
        api = CorpApi(self.corpid, self.secret)
        try:
            response = api.httpCall(
                CORP_API_TYPE['DEPARTMENT_LIST'],
                {
                    'id': self.department_id,
                }
            )
            for obj in response['department']:
                # 查询数据库是否存在相同的企业微信部门ID，有则更新，无则新建
                records = self.department.search([
                    ('wxwork_department_id', '=', obj['id']),
                    ('is_wxwork_department', '=', True)],
                    limit=1)
                if len(records) > 0:
                    self.update_department(records, obj)
                else:
                    self.create_department(records, obj)
            # 由于json数据是无序的，故在同步到本地数据库后，需要设置新增企业微信部门的上级部门
            # self.set_parent_department()
        except BaseException:
            self.result = False
        return self.result

    def create_department(self, records, obj):
        records.create({
            'name': obj['name'],
            'wxwork_department_id': obj['id'],
            'wxwork_department_parent_id': obj['parentid'],
            'wxwork_department_order': obj['order'],
            'is_wxwork_department': True
        })
        self.result = True

    def update_department(self, records, obj):
        records.write({
            'name': obj['name'],
            'wxwork_department_parent_id': obj['parentid'],
            'wxwork_department_order': obj['order'],
            'is_wxwork_department': True
        })
        self.result = True

class SetDepartment(object):
    def __init__(self,  department):
        self.department = department
        self.result = None

    def set_parent_department(self):
        """由于json数据是无序的，故在同步到本地数据库后，需要设置新增企业微信部门的上级部门"""
        try:
            departments = self.department.search(
                [('is_wxwork_department', '=', True)])
            for dep in departments:
                if not dep.wxwork_department_id:
                    pass
                else:
                    # self.update_department_parent_id(dep)
                    parent_department = self.department.search([
                        ('wxwork_department_id', '=', dep.wxwork_department_parent_id),
                        ('is_wxwork_department', '=', True)
                    ])
                    dep.write({
                        'parent_id': parent_department.id,
                    })
            self.result = True
        except BaseException:
            self.result = False
        return self.result

    def get_parent_department(self,dep):
        parent_department = self.department.search([
            ('wxwork_department_id', '=', dep.wxwork_department_parent_id),
            ('is_wxwork_department', '=', True)
        ])
        return parent_department

    def update_department_parent_id(self, dep):
        parent_dep = self.get_parent_department(dep)
        dep.write({
            'parent_id': parent_dep.id
        })
        self.result = True

class SyncImage(object):
    def __init__(self, corpid, secret, department_id, file_path):
        self.corpid = corpid
        self.secret = secret
        self.department_id = department_id
        self.file_path = file_path
        self.result = None

    def download_image(self):
        api = CorpApi(self.corpid, self.secret)
        response = api.httpCall(
            CORP_API_TYPE['USER_LIST'],
            {
                'department_id': self.department_id,
                'fetch_child': '1',
            }
        )
        self.download_image_avatar(response['userlist'])
        self.download_image_qr_code(response['userlist'])

        return self.result

    def check_identical_images(self,remote,local):
        '''
        比较远程图片和本地图片是否一致
        :param remote: 远程图片
        :param local: 本地图片
        :return: 布尔值
        '''
        try:
            resp = urllib.request.urlopen(remote)
            remote_img = np.asarray(bytearray(resp.read()), dtype="uint8")
            remote_img = cv2.imdecode(remote_img, cv2.IMREAD_COLOR)

            local_img = cv2.imread(local)

            difference = cv2.subtract(remote_img, local_img)
            result = not np.any(difference)
            if result is True:
                return True
            else:
                return False
        except BaseException as e:
            print(e)

    def path_is_exists(self,path):
        '''
        检文件夹路径
        :param path:
        :return:
        '''
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def download_image_avatar(self,response):
        directory = self.file_path + "/avatar//"
        self.path_is_exists(directory)
        for obj in response:
            remote_img = obj['avatar']
            local_img = directory + obj['userid'] + ".jpg"
            if os.path.exists(local_img):
                if not self.check_identical_images(remote_img,local_img):
                    try:
                        avatar_data = urllib.request.urlopen(remote_img).read()  # 打开URL
                        file_avatar = open(local_img, "wb")  # 读取，写入
                        file_avatar.write(avatar_data)
                        file_avatar.close()
                    except BaseException as e:
                        print('头像错误-%s %s' %(obj['name'],e))
                        pass
                    print("头像图片不一致")
                else:
                    pass
                    print("头像图片一致")
            else:
                try:
                    avatar_data = urllib.request.urlopen(remote_img).read()  # 打开URL
                    file_avatar = open(local_img, "wb")  # 读取，写入
                    file_avatar.write(avatar_data)
                    file_avatar.close()
                except BaseException as e:
                    print('头像错误-%s %s' % (obj['name'], e))
                    pass

        self.result = True


    def download_image_qr_code(self,response):
        directory = self.file_path + "/qr_code//"
        self.path_is_exists(directory)
        for obj in response:
            remote_img = obj['qr_code']
            local_img = directory + obj['userid'] + ".png"
            if os.path.exists(local_img):
                if not self.check_identical_images(remote_img, local_img):
                    try:
                        qr_code_data = urllib.request.urlopen(remote_img).read()  # 打开URL
                        file_qr_code = open(local_img, "wb")  # 读取，写入
                        file_qr_code.write(qr_code_data)
                        file_qr_code.close()
                    except BaseException as e:
                        print('二维码错误-%s %s' % (obj['name'], e))
                        pass
                    print("二维码图片不一致")
                else:
                    pass
                    print("二维码图片一致")
            else:
                try:
                    qr_code_data = urllib.request.urlopen(remote_img).read()  # 打开URL
                    file_qr_code = open(local_img, "wb")  # 读取，写入
                    file_qr_code.write(qr_code_data)
                    file_qr_code.close()
                except BaseException as e:
                    print('二维码错误-%s %s' % (obj['name'], e))
                    pass

        self.result = True

class SyncEmployee(object):
    def __init__(self, corpid, secret, department_id, department, employee, sync_img):
        self.corpid = corpid
        self.secret = secret
        self.department_id = department_id
        self.department = department
        self.employee = employee
        self.sync_img = sync_img
        self.result = None

    def sync_employee(self):
        api = CorpApi(self.corpid, self.secret)
        try:
            response = api.httpCall(
                CORP_API_TYPE['USER_LIST'],
                {
                    'department_id': self.department_id,
                    'fetch_child': '1',
                }
            )
            for obj in response['userlist']:
                # 查询数据库是否存在相同的企业微信部门ID，有则更新，无则新建
                domain = ['|', ('active', '=', False),
                          ('active', '=', True)]
                records = self.employee.search(
                    domain +[
                        ('userid', '=', obj['userid']),
                        ('is_wxwork_employee', '=', True)],
                    limit=1)
                if len(records) > 0:
                    self.update_employee(records, obj)
                else:
                    self.create_employee(records, obj)

        except BaseException:
            self.result = False
        return self.result

    def create_employee(self,records, obj):
        department_ids = []
        for department in obj['department']:
            department_ids.append(self.get_employee_parent_department(department))
        # if not self.sync_img:
        #     avatar = None
        # else:
        #     # avatar = self.encode_image_as_base64(obj['avatar'],"d:\img\\",obj['userid'])
        #     avatar = self.encode_image_as_base64(obj['avatar'])
        #     # avatar = Common(obj['avatar']).avatar2image()

        records.create({
            'userid': obj['userid'],
            'name': obj['name'],
            'gender': Common(obj['gender']).gender(),
            'marital': None, # 不生成婚姻状况
            # 'image': avatar,
            'mobile_phone': obj['mobile'],
            'work_phone': obj['telephone'],
            'work_email': obj['email'],
            'active': obj['enable'],
            'alias': obj['alias'],
            'department_ids': [(6, 0, department_ids)],
            'wxwork_user_order': obj['order'],
            # 'qr_code': Common(obj['qr_code']).avatar2image(),
            # 'qr_code': self.encode_image_as_base64(obj['qr_code'],"d:\\img\\",obj['userid']),
            'is_wxwork_employee': True,
        })
        self.result =True

    def update_employee(self,records, obj):
        department_ids = []
        for department in obj['department']:
            department_ids.append(self.get_employee_parent_department(department))

        records.write({
            'name': obj['name'],
            'gender': Common(obj['gender']).gender(),
            'mobile_phone': obj['mobile'],
            'work_phone': obj['telephone'],
            'work_email': obj['email'],
            'active': obj['enable'],
            'alias': obj['alias'],
            'department_ids': [(6, 0, department_ids)],
            'wxwork_user_order': obj['order'],
            'is_wxwork_employee': True
        })
        self.result = True

    def get_employee_parent_department(self,department_id):
        try:
            departments = self.department.search([
                ('wxwork_department_id', '=', department_id),
                ('is_wxwork_department', '=', True)],
                limit=1)
            if len(departments) > 0:
                return departments.id
        except BaseException:
            pass

    def update_leave_employee(self):
        """
        比较企业微信和odoo的员工数据，且设置离职odoo员工active状态
        """
        api = CorpApi(self.corpid, self.secret)
        try:
            response = api.httpCall(
                CORP_API_TYPE['USER_LIST'],
                {
                    'department_id': self.department_id,
                    'fetch_child': '1',
                }
            )
            list_user = []
            list_employee = []
            for obj in response['userlist']:
                list_user.append(obj['userid'])

            domain = ['|', ('active', '=', False),
                      ('active', '=', True)]
            records = self.employee.search(
                domain + [
                    ('is_wxwork_employee', '=', True)
                ])

            for obj in records:
                list_employee.append(obj.userid)

            list_user_leave = list(set(list_employee).difference(set(list_user)))

            for obj in list_user_leave:
                employee = records.search([
                    ('userid', '=', obj)
                ])
                self.set_employee_active(employee)
            self.result = True
        except BaseException:
            self.result = False
        return self.result

    def set_employee_active(self,records):
        records.write({
            'active': False,
        })
        self.result = True

class SyncEmployeeToUser(object):
    def __init__(self, employee, user, group, sync_img):
        self.employee = employee
        self.user = user
        self.group = group
        self.sync_img = sync_img
        # self.provider = provider
        self.result = None

    def sync_user(self):
        domain = ['|', ('active', '=', False),
                  ('active', '=', True)]
        employee = self.employee.search(
            domain + [
                ('is_wxwork_employee', '=', True)])
        try:
            for records in employee:
                user = self.user.search(
                    domain + [
                        ('userid', '=', records.userid),
                        ('is_wxwork_user', '=', True)
                    ],limit=1
                )
                if len(user) > 0:
                    self.update_user(records, user)
                else:
                    self.create_user(records, user, self.group)
        except BaseException:
            self.result = False
        return self.result

    def create_user(self, employee, user ,group):
        groups_id = group.search([('id', '=', 9),],limit=1).id
        #TODO 空邮件需要处理
        email = "" if not employee.work_email else employee.work_email
        # print(email)
        # oauth_provider_id = provider.search([('name', '=', '企业微信一键登录'),],limit=1).id

        if not self.sync_img:
            image = None
        else:
            image = employee.image
        user.create({
            'name': employee.name,
            'login': employee.userid,
            'password':Common(8).random_passwd(),
            # 'oauth_uid': employee.userid,
            # 'oauth_provider_id': oauth_provider_id,
            'email': email,
            'userid': employee.userid,
            'image': image,
            'qr_code': employee.qr_code,
            'active': employee.active,
            'wxwork_user_order': employee.wxwork_user_order,
            'mobile': employee.mobile_phone,
            'phone': employee.work_phone,
            'is_wxwork_user': True,
            'is_moderator': False,
            'is_company': False,
            'supplier': False,
            'employee': True,
            'share': False,
            'groups_id': [(6, 0, [groups_id])], #设置用户为门户用户
        })
        self.result = True

    def update_user(self, employee, user):
        user.write({
            'name': employee.name,
            'active': employee.active,
            # 'oauth_uid': employee.userid,
            'wxwork_user_order': employee.wxwork_user_order,
            'is_wxwork_user': True,
            'employee': True,
            'mobile': employee.mobile_phone,
            'phone': employee.work_phone,
        })

        self.result = True

class EmployeeBindingUser(object):
    def __init__(self, employee, user):
        self.employee = employee
        self.user = user
        self.result = None

    def binding(self):
        domain = ['|', ('active', '=', False),
                  ('active', '=', True)]
        employee = self.employee.search(
            domain + [
                ('is_wxwork_employee', '=', True)])
        try:
            for records in employee:
                user = self.user.search(
                    domain + [
                        ('userid', '=', records.userid),
                        ('is_wxwork_user', '=', True)
                    ], limit=1
                )
                if len(user) > 0:
                    self.set_employee_user_id(records, user)
                else:
                    pass
        except BaseException:
            self.result = False
        return self.result

    def set_employee_user_id(self, employee, user):
        employee.write({
            'user_id': user.id,
        })
        self.result = True

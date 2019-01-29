# -*- coding: utf-8 -*-

from ..api.CorpApi import *
from ..helper.common import *
import platform
import base64,urllib,os,platform,cv2
import numpy as np
import requests
import time
from threading import Thread
from multiprocessing.dummy import Pool as ThreadPool

# start 以下为解决 image file is truncated (18 bytes not processed)错误
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
# end 以上为解决 image file is truncated (18 bytes not processed)错误

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


    def run(self):
        if (platform.system() == 'Windows'):
            avatar_directory = self.file_path.replace("\\", "/") + "avatar/"
            qr_code_directory = self.file_path.replace("\\", "/") + "qr_code/"
        else:
            avatar_directory = self.file_path + "avatar/"
            qr_code_directory = self.file_path + "qr_code/"
        self.path_is_exists(avatar_directory)
        self.path_is_exists(qr_code_directory)

        user_list,avatar_urls,qr_code_urls = self.generate_image_list()

        start = time.time()
        for i in range(len(user_list)):
            remote_avatar_img = avatar_urls[i]
            local_avatar_img = avatar_directory + user_list[i]+ ".jpg"

            remote_qr_code_img = qr_code_urls[i]
            local_qr_code_img = qr_code_directory + user_list[i]+ ".png"

            t1 = Thread(target=self.check_image, args=[remote_avatar_img,local_avatar_img])
            t1.start()
            t2 = Thread(target=self.check_image, args=[remote_qr_code_img, local_qr_code_img])
            t2.start()
            # self.check_image(remote_avatar_img,local_avatar_img)
            # self.check_image(remote_qr_code_img,local_qr_code_img)
        end = time.time()
        print('Total cost:', end - start, 's')

    def generate_image_list(self):
        '''
        生成userid、avatar、qr_code的List
        :return: list
        '''
        api = CorpApi(self.corpid, self.secret)
        response = api.httpCall(
            CORP_API_TYPE['USER_LIST'],
            {
                'department_id': self.department_id,
                'fetch_child': '1',
            }
        )
        userid_list = []
        avatar_urls = []
        qr_code_urls = []
        for object in response['userlist']:
            userid_list.append(object['userid'])
            avatar_urls.append(object['avatar'])
            qr_code_urls.append(object['qr_code'])
        return userid_list,avatar_urls,qr_code_urls

    def path_is_exists(self,path):
        '''
        检文件夹路径
        :param path:
        :return:
        '''
        if not os.path.exists(path):
            os.makedirs(path)
        return path

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
            return False
            # print(e)

    def check_image(self,remote_img,local_img):
        # 是否存在本地图片
        if os.path.exists(local_img):
            # 比较本地远程和本地图片
            if not self.check_identical_images(remote_img, local_img):
                self.download_image(remote_img, local_img)
        else:
            self.download_image(remote_img, local_img)

    def download_image(self,remote_img,local_img):
        try:
            avatar_data = urllib.request.urlopen(remote_img).read()  # 打开URL
            file_avatar = open(local_img, "wb")  # 读取，写入
            file_avatar.write(avatar_data)
            file_avatar.close()
        except BaseException as e:
            # print('头像错误-%s %s' %(obj['name'],e))
            pass


class SyncEmployee(object):
    def __init__(self, corpid, secret, department_id, department, employee, sync_img, img_path):
        self.corpid = corpid
        self.secret = secret
        self.department_id = department_id
        self.department = department
        self.employee = employee
        self.sync_img = sync_img
        self.img_path = img_path
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
                        ('wxwork_id', '=', obj['userid']),
                        ('is_wxwork_employee', '=', True)],
                    limit=1)
                if len(records) > 0:
                    self.update_employee(records, obj)
                else:
                    self.create_employee(records, obj)

        except BaseException:
            self.result = False
        return self.result

    def encode_image_as_base64(self,image_path):
        # if not self.sync_img:
        #     return None
        if not os.path.exists(image_path):
            return None
        else:
            try:
                with open(image_path, "rb") as f:
                    encoded_string = base64.b64encode(f.read())
                return encoded_string
            except BaseException as e:
                return None
                # pass

    def create_employee(self,records, obj):
        department_ids = []
        for department in obj['department']:
            department_ids.append(self.get_employee_parent_department(department))

        if (platform.system() == 'Windows'):
            avatar_file = self.img_path.replace("\\","/") + "/avatar/" + obj['userid'] + ".jpg"
            qr_code_file = self.img_path.replace("\\","/")  + "/qr_code/" + obj['userid'] + ".png"
        else:
            avatar_file = self.img_path + "avatar/" + obj['userid'] + ".jpg"
            qr_code_file = self.img_path + "qr_code/" + obj['userid'] + ".png"

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
        except BaseException as e:
            print('%s - %s' % (obj['name'], e))
        self.result =True

    def update_employee(self,records, obj):
        department_ids = []
        for department in obj['department']:
            department_ids.append(self.get_employee_parent_department(department))

        if (platform.system() == 'Windows'):
            avatar_file = self.img_path.replace("\\","/") + "/avatar/" + obj['userid'] + ".jpg"
            qr_code_file = self.img_path.replace("\\","/")  + "/qr_code/" + obj['userid'] + ".png"
        else:
            avatar_file = self.img_path + "avatar/" + obj['userid'] + ".jpg"
            qr_code_file = self.img_path + "qr_code/" + obj['userid'] + ".png"

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

            for e in records:
                list_employee.append(e.wxwork_id)

            list_user_leave = list(set(list_employee).difference(set(list_user)))

            for obj in list_user_leave:
                employee = records.search([
                    ('wxwork_id', '=', obj)
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
    def __init__(self, employee, user, group):
        self.employee = employee
        self.user = user
        self.group = group
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
                        ('wxwork_id', '=', records.wxwork_id),
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

        if not employee.image:
            image = None
        else:
            image = employee.image
        user.create({
            'name': employee.name,
            'login': employee.wxwork_id,
            'oauth_uid': employee.wxwork_id,
            'password':Common(8).random_passwd(),
            'email': email,
            'wxwork_id': employee.wxwork_id,
            'image': image,
            # 'qr_code': employee.qr_code,
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
            'oauth_uid': employee.wxwork_id,
            'active': employee.active,
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
                        ('wxwork_id', '=', records.wxwork_id),
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

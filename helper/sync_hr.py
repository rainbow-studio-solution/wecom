# -*- coding: utf-8 -*-
import base64
import logging
from urllib.request import urlopen
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
from .common import *
from ..api.CorpApi import *
from odoo import fields

import logging
_logger = logging.getLogger(__name__)

class Contacts(object):
    """
    同步企微通讯录到HR操作类
    """

    def __init__(self, corpid, secret, department_id, department, employee, sync_del_hr,):
        self.corpid = corpid
        self.secret = secret
        self.department_id = department_id
        self.department = department
        self.employee = employee
        self.sync_del_hr = sync_del_hr
        self.result = None

    def sync(self):
        api = CorpApi(self.corpid, self.secret)
        try:
            dep_response = api.httpCall(
                CORP_API_TYPE['DEPARTMENT_LIST'],
                {
                    'id': self.department_id,
                }
            )
            employee_response = api.httpCall(
                CORP_API_TYPE['USER_LIST'],
                {
                    'department_id': self.department_id,
                    'fetch_child': '1',
                }
            )
            self.sync_contacts(
                dep_response, employee_response, self.department, self.employee)
            self.result = True
        except BaseException:
            return False
        return self.result

    def sync_contacts(self, dep_response, employee_response, Department, Employee):
        """同步通讯录"""
        #同步HR
        if Common(self.sync_del_hr).str_to_bool():
            # 删除数据
            self.del_employee_data(
                dep_response['department'],
                employee_response['userlist'],
                Department,
                Employee)
        else:
            for obj in dep_response['department']:
                # 查询数据库是否存在相同的企业微信部门ID，有则更新，无则新建
                department_records = Department.search([
                    ('wxwork_department_id', '=', obj['id']),
                    ('is_wxwork_department', '=', True)],
                    limit=1)
                if len(department_records) > 0:
                    self._update_department(department_records, obj)
                else:
                    self._create_department(department_records, obj)

            # 由于json数据是无序的，故在同步到本地数据库后，需要设置新增企业微信部门的上级部门
            self._set_parent_department(Department)

            for obj in employee_response['userlist']:
                # 查询hr_employee是否存在相同的企业微信用户ID，有则更新，无则新建,以及重新设置active状态
                domain = ['|', ('active', '=', False),
                          ('active', '=', True)]
                employee_records = Employee.search(
                    domain + [
                        ('userid', '=', obj['userid']),
                        ('is_wxwork_user', '=', True)
                    ],
                    limit=1)
                if len(employee_records) > 0:
                    self._update_employee(employee_records, obj)
                else:
                    self._create_employee(employee_records, obj)

    def del_employee_data(
            self,
            dep_response,
            employee_response,
            Department,
            Employee):
        """
        比较且设置employee数据active状态
        """
        list_user = []
        list_employee = []
        for json_obj in employee_response:
            list_user.append(json_obj['userid'])

        domain = ['|', ('active', '=', False),
                  ('active', '=', True)]
        records = Employee.search(
            domain + [
                ('is_wxwork_user', '=', True)
            ])

        for employee_obj in records:
            list_employee.append(employee_obj.userid)

        list_user_del = list(set(list_employee).difference(set(list_user)))

        for obj in list_user_del:
            userids = records.search([
                ('userid', '=', obj)
            ])
            userids.unlink()  # 执行删除

    def _update_employee(self, records, obj):
        """
        更新企业微信用户资料
        """
        department_ids = []
        for department in obj['department']:
            department_ids.append(self._get_user_parent_department(department))
        records.write({
            'name': obj['name'],
            'gender': Common(obj['gender']).gender(),
            'image': Common(obj['avatar']).avatar2image(),
            'mobile_phone': obj['mobile'],
            'work_phone': obj['telephone'],
            'work_email': obj['email'],
            'active': obj['enable'],
            'alias': obj['alias'],
            'department_ids': [(6, 0, department_ids)],
            'wxwork_user_order': obj['order'],
            'is_wxwork_user': True
        })

    def _create_employee(self, records, obj):
        """
        创建企业微信用户资料
        """
        # department_ids = []
        # for department in obj['department']:
        #     department_ids.append(self._get_user_parent_department(department))

        records.create({
            'userid': obj['userid'],
            'name': obj['name'],
            # 'gender': Common(obj['gender']).gender(),
            # 'marital': not fields,  # 不生成婚姻状况
            # 'image': Common(obj['avatar']).avatar2image(),
            # 'image': self._avatar2image(obj['avatar']),
            # 'mobile_phone': obj['mobile'],
            # 'work_phone': obj['telephone'],
            # 'work_email': obj['email'],
            # 'active': obj['enable'],
            # 'alias': obj['alias'],
            # 'department_ids': [(6, 0, department_ids)],
            # 'wxwork_user_order': obj['order'],
            'is_wxwork_user': True
        })
        _logger.info("创建" + obj['name'])

    def _update_department(self, records, obj):
        """
        更新企业微信部门资料
        """
        records.write({
            'name': obj['name'],
            'wxwork_department_parent_id': obj['parentid'],
            'wxwork_department_order': obj['order'],
            'is_wxwork_department': True
        })

    def _create_department(self, records, obj):
        """
        创建企业微信部门资料
        """
        records.create({
            'name': obj['name'],
            'wxwork_department_id': obj['id'],
            'wxwork_department_parent_id': obj['parentid'],
            'wxwork_department_order': obj['order'],
            'is_wxwork_department': True
        })

    def _get_user_parent_department(self, department_id):
        """
        获取odoo上级部门
        :param Employee:
        :param Department:
        :return:
        """
        try:
            Department = self.department
            departments = Department.search([
                ('wxwork_department_id', '=', department_id),
                ('is_wxwork_department', '=', True)],
                limit=1)
            if len(departments) > 0:
                return departments.id
        except BaseException:
            pass

    def _set_parent_department(self, Department):
        """
        设置企业微信部门的上级部门
        """
        try:
            departments = Department.search(
                [('is_wxwork_department', '=', True)])
            for department in departments:
                if not department.wxwork_department_id:
                    pass
                else:
                    if not department.wxwork_department_parent_id:
                        pass
                    else:
                        parent_department = Department.search([
                            ('wxwork_department_id', '=', department.wxwork_department_parent_id),
                            ('is_wxwork_department', '=', True)
                        ])
                        department.write({
                            'parent_id': parent_department.id,
                        })
            return True
        except BaseException:
            raise ValidationError('设置上级部门失败！')

    def _avatar2image(self, url):
        """
            头像转换
        """
        if not url:
            pass
        else:
            # res = requests.get(url)
            return base64.b64encode(urlopen(url).read())
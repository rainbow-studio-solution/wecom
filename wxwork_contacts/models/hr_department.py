# -*- coding: utf-8 -*-

from odoo import api, fields, models
from ..api.CorpApi import *
from ..helper.common import *
import logging,platform
from threading import Thread, Lock
import time


class HrDepartment(models.Model):
    _inherit = 'hr.department'
    _description = '企业微信部门'
    _order = 'wxwork_department_id'

    # name = fields.Char('微信部门名称',help='长度限制为1~32个字符，字符不能包括\:?”<>｜')
    wxwork_department_id = fields.Integer(
        '企微部门ID', default=0, help='企业微信部门ID', readonly=True,)
    wxwork_department_parent_id = fields.Integer(
        '企微上级部门ID', default=1, help='上级部门id,32位整型。根部门为1', readonly=True,)
    wxwork_department_order = fields.Char(
        '企微部门排序',
        default='1',
        help='在父部门中的次序值。order值大的排序靠前。值范围是[0, 2^32)',
        readonly=True,
    )
    is_wxwork_department = fields.Boolean('企微部门', readonly=True)

class SyncDepartment(models.Model):
    _inherit = 'hr.department'
    _description = '同步企业微信部门'

    @api.multi
    def sync_department(self):
        params = self.env['ir.config_parameter'].sudo()
        corpid = params.get_param('wxwork.corpid')
        secret = params.get_param('wxwork.contacts_secret')
        sync_department_id = params.get_param('wxwork.contacts_sync_hr_department_id')
        api = CorpApi(corpid, secret)
        try:
            response = api.httpCall(
                CORP_API_TYPE['DEPARTMENT_LIST'],
                {
                    'id': sync_department_id,
                }
            )
            start = time.time()
            threaded_set = Thread(target=self.run_set, args=[])
            for obj in response['department']:
                threaded_sync = Thread(target=self.run_sync, args=[obj])
                threaded_sync.start()
                # self.run(obj)
                if threaded_sync.is_alive():
                    print("执行中")
                else:

                    threaded_set.start()
                    end = time.time()
                    times = end - start
                    print(times)

            result = True
        except BaseException as e:
            print(repr(e))
            result = False
        return times, result

    @api.multi
    def run_sync(self, obj):
        with api.Environment.manage():
            new_cr = self.pool.cursor()
            self = self.with_env(self.env(cr=new_cr))
            env = self.sudo().env['hr.department']
            # 查询数据库是否存在相同的企业微信部门ID，有则更新，无则新建
            records = env.search([
                ('wxwork_department_id', '=', obj['id']),
                ('is_wxwork_department', '=', True)],
                limit=1)
            try:
                if len(records) > 0:
                    self.update_department(records, obj)
                else:
                    self.create_department(records, obj)
            except Exception as e:
                print(repr(e))


            new_cr.commit()
            new_cr.close()

    @api.multi
    def create_department(self, records, obj):
        try:
            records.create({
                'name': obj['name'],
                'wxwork_department_id': obj['id'],
                'wxwork_department_parent_id': obj['parentid'],
                'wxwork_department_order': obj['order'],
                'is_wxwork_department': True
            })
            result = True
        except Exception as e:
            print('部门:%s - %s' % (obj['name'], repr(e)))
            result = False
        return result

    @api.multi
    def update_department(self, records, obj):
        try:
            records.write({
                'name': obj['name'],
                'wxwork_department_parent_id': obj['parentid'],
                'wxwork_department_order': obj['order'],
                'is_wxwork_department': True
            })
            result = True
        except Exception as e:
            print('部门:%s - %s' % (obj['name'], repr(e)))
            result = False
        return result

    @api.multi
    def run_set(self):
        """由于json数据是无序的，故在同步到本地数据库后，需要设置新增企业微信部门的上级部门"""
        with api.Environment.manage():
            new_cr = self.pool.cursor()
            self = self.with_env(self.env(cr=new_cr))
            env = self.sudo().env['hr.department']
            departments = env.search(
                [('is_wxwork_department', '=', True)])
            try:
                for dep in departments:
                    if not dep.wxwork_department_id:
                        pass
                    else:
                        dep.write({
                            'parent_id': self.get_parent_department(dep,departments).id,
                        })
                result = True
            except BaseException as e:
                print('部门:%s 的上级部门设置失败 - %s' % (dep.name, repr(e)))
                result = False
            new_cr.commit()
            new_cr.close()

            return  result

    @api.multi
    def get_parent_department(self,dep,departments):
        parent_department = departments.search([
            ('wxwork_department_id', '=', dep.wxwork_department_parent_id),
            ('is_wxwork_department', '=', True)
        ])
        return parent_department

    # @api.multi
    # def update_department_parent_id(self, dep, departments):
    #     parent_department = departments.search([
    #         ('wxwork_department_id', '=', dep.wxwork_department_parent_id),
    #         ('is_wxwork_department', '=', True)
    #     ])
    #     dep.write({
    #         'parent_id': parent_department.id,
    #     })

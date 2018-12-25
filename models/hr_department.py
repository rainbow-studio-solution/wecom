# -*- coding: utf-8 -*-

import logging
from ..api.CorpApi import *
from ..api.api_errcode import *
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


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
    is_wxwork_department = fields.Boolean('企微部门')
    # is_wxwork_department = fields.Boolean('企微部门', readonly=True)



    @api.model
    def sync_department(self,json):
        '''同步部门'''
        for obj in json['department']:
            records = self.search([
                ('wxwork_department_id', '=', json['id']),
                ('is_wxwork_department', '=', True)],
                limit=1)
            if len(records)>0:
                self.update(obj)
            else:
                self.create(obj)
        return super(HrDepartment, self).sync_department(json)

    @api.model_create_multi
    def create(self,json):
        """创建企业微信部门资料 """
        self.env['hr.department'].create({
            'name': json['name'],
            'wxwork_department_id': json['id'],
            'wxwork_department_parent_id': json['parentid'],
            'wxwork_department_order': json['order'],
            'is_wxwork_department': True
        })
        return super(HrDepartment,self).create(json)

    @api.multi
    def update(self, json):
        """
        更新企业微信部门资料
        """
        self.write({
            'name': json['name'],
            'wxwork_department_parent_id': json['parentid'],
            'wxwork_department_order': json['order'],
            'is_wxwork_department': True
        })

    @api.multi
    def _get_user_parent_department(self, department_id):
        """        获取odoo上级部门        """
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

    def set_parent_department(self, Department):
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


    @api.multi
    def unlink(self):
        params = self.env['ir.config_parameter'].sudo()
        edit = params.get_param('wxwork.contacts_edit_enabled')
        # 判断是否开启 允许API编辑通讯录
        if not edit:
            return super(HrDepartment, self).unlink()  # 直接删除hr.department数据
        else:
            params = self.env['ir.config_parameter'].sudo()
            corpid = params.get_param('wxwork.corpid')
            secret = params.get_param('wxwork.contacts_secret')
            api = CorpApi(corpid, secret)
            for record in self:
                if self.search([('parent_id', '=', record.id)]):
                    # 判断是否有子部门
                    raise UserError('请先删除【 %s 】的子部门!' % record.name)
                else:
                    try:
                        response = api.httpCall(
                            CORP_API_TYPE['DEPARTMENT_DELETE'],
                            {
                                'id': record.wxwork_department_id,
                            }
                        )
                        err_code = response['errcode']
                        err_msg = response['errmsg']
                        if err_code == 0 and err_msg == 'deleted':
                            return super(HrDepartment, self).unlink()
                        else:
                            raise UserError(
                                '删除部门【 %s 】失败!，\n原因：%s %s' %
                                (record.name, err_code, Errcode.getErrcode(err_code)))
                    except ApiException as e:
                        raise ValidationError(
                            '错误：%s %s\n 详细信息：%s' %
                            (str(e.errCode), Errcode.getErrcode(e.errCode), e.errMsg))
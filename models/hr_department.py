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
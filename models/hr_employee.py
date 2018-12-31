# -*- coding: utf-8 -*-

from odoo import api, fields, models, registry, SUPERUSER_ID

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _description = '企业微信员工'
    _order = 'wxwork_user_order'

    userid = fields.Char(string='企微用户Id', readonly=True)
    alias = fields.Char(string='别名')
    department_ids = fields.Many2many('hr.department', string='企微多部门')
    qr_code = fields.Binary(string='个人二维码', help='员工个人二维码，扫描可添加为外部联系人', readonly=True)
    wxwork_user_order = fields.Char(
        '企微用户排序',
        default='0',
        help='部门内的排序值，默认为0。数量必须和department一致，数值越大排序越前面。值范围是[0, 2^32)',
        readonly=True,
    )

    is_wxwork_employee = fields.Boolean('企微员工', readonly=True)

    # @api.model
    # def sync(self):
    #     '''同步员工'''
    #     params = self.env['ir.config_parameter'].sudo()
    #     corpid = params.get_param('wxwork.corpid')
    #     secret = params.get_param('wxwork.contacts_secret')
    #     sync_department_id = params.get_param('wxwork.contacts_sync_hr_department_id')
    #     sync_del_hr = params.get_param('wxwork.contacts_sync_del_hr_enabled')
    #
    #     api = CorpApi(corpid, secret)
    #     json = api.httpCall(
    #         CORP_API_TYPE['USER_LIST'],
    #         {
    #             'department_id': sync_department_id,
    #             'fetch_child': '1',
    #         }
    #     )
    #
    #     for obj in json['userlist']:
    #         records = self.search([
    #             ('userid', '=', obj['userid']),
    #             ('is_wxwork_employee', '=', True)],
    #             limit=1)
    #         if len(records) > 0:
    #             self.update(obj)
    #         else:
    #             self.create(obj)
    #
    #     # self.set_leave_employee(json)
    #     # self.sync_user_from_employee()
    #
    # @api.multi
    # def create(self, json):
    #     '''创建员工'''
    #     department_ids = []
    #     for department in json['department']:
    #         department_ids.append(self.get_employee_parent_department(department))
    #     lines = super(HrEmployee, self).create({
    #         'userid': json['userid'],
    #         'name': json['name'],
    #         'gender': Common(json['gender']).gender(),
    #         'marital': not fields,  # 不生成婚姻状况
    #         # 'image': Common(json['avatar']).avatar2image(),
    #         'mobile_phone': json['mobile'],
    #         'work_phone': json['telephone'],
    #         'work_email': json['email'],
    #         'active': json['enable'],
    #         'alias': json['alias'],
    #         'department_ids': [(6, 0, department_ids)],
    #         'wxwork_user_order': json['order'],
    #         'qr_code': Common(json['qr_code']).avatar2image(),
    #         'is_wxwork_employee': True
    #     })
    #     return lines
    #
    # @api.multi
    # def update(self, json):
    #     '''更新员工'''
    #     department_ids = []
    #     for department in json['department']:
    #         department_ids.append(self.get_employee_parent_department(department))
    #     super(HrEmployee, self).write({
    #         'name': json['name'],
    #         'gender': Common(json['gender']).gender(),
    #         # 'image': Common(json['avatar']).avatar2image(),
    #         'mobile_phone': json['mobile'],
    #         'work_phone': json['telephone'],
    #         'work_email': json['email'],
    #         'active': json['enable'],
    #         'alias': json['alias'],
    #         'department_ids': [(6, 0, department_ids)],
    #         'wxwork_user_order': json['order'],
    #         # 'qr_code': Common(json['qr_code']).avatar2image(),
    #         'is_wxwork_employee': True
    #     })
    #
    # @api.multi
    # def get_employee_parent_department(self, department_id):
    #     """
    #     获取odoo上级部门
    #     """
    #     try:
    #         Department = self.env['hr.department']
    #         departments = Department.search([
    #             ('wxwork_department_id', '=', department_id),
    #             ('is_wxwork_department', '=', True)],
    #             limit=1)
    #         if len(departments) > 0:
    #             return departments.id
    #     except BaseException:
    #         pass
    #
    # @api.multi
    # def set_leave_employee(self, json):
    #     """
    #     比较企业微信和odoo的员工数据，且设置离职odoo员工active状态
    #     """
    #     list_user = []
    #     list_employee = []
    #     for obj in json:
    #         list_user.append(obj['userid'])
    #
    #     domain = ['|', ('active', '=', False),
    #               ('active', '=', True)]
    #     records = self.search(
    #         domain + [
    #             ('is_wxwork_employee', '=', True)
    #         ])
    #
    #     for obj in records:
    #         list_employee.append(obj.userid)
    #
    #     list_user_leave = list(set(list_employee).difference(set(list_user)))
    #
    #     for obj in list_user_leave:
    #         userids = records.search([
    #             ('userid', '=', obj)
    #         ])
    #         userids.write({
    #             'active': False,
    #         })

    # @api.multi
    # def sync_user_from_employee(self, user):
    #     vals = dict(
    #         name=user.name,
    #         image=user.image,
    #         work_email=user.email,
    #         is_wxwork_user =True
    #     )
    #     if user.tz:
    #         vals['tz'] = user.tz
    #     return vals
    #
    # @api.multi
    # def create_user(self, vals):
    #     user = self.env['res.users'].sudo().create({
    #         'name': vals.name,
    #         'login': vals.userid,
    #         # "email": employee.work_email,
    #         # 'userid': employee.userid,
    #         # 'image': employee.image,
    #         # 'qr_code': employee.qr_code,
    #         # 'active': employee.active,
    #         # 'wxwork_user_order': employee.wxwork_user_order,
    #         # 'is_wxwork_user': True,
    #     })
    #
    #
    # @api.multi
    # def update_user(self,employee):
    #     # print("更新" + self.name)
    #     self.env['res.users'].write({
    #         'name': employee.name,
    #         "email": employee.work_email,
    #         'active': employee.active,
    #         'wxwork_user_order': employee.wxwork_user_order,
    #     })
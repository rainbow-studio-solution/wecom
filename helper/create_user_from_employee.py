# -*- coding: utf-8 -*-


from .common import *
from odoo import fields
from ..api.CorpApi import *
from odoo import api, SUPERUSER_ID


class CreateOrUpdateUserFromEmployee(object):
    """
    从Employee创建和更新User
    """

    def __init__(self, employee):
        self.employee = employee
        self.result = None

    def _create_user(self, cr, user, employee):
        env = api.Environment(cr, SUPERUSER_ID, {})
        object = env['res.users'].search([('dashboard_graph_model', '=', 'crm.opportunity.report')])
        employee.user_id = object.create({
            'dashboard_graph_model': None
        })

    def CreateOrUpdate(self,cr, registry):
        env = api.Environment(cr, SUPERUSER_ID, {})
        domain = ['|', ('active', '=', False),
                  ('active', '=', True)]
        user = env['res.users'].search(domain)
        try:
            for employee in self.employee:
                records = user.search([
                    ('userid', '=', employee.userid)
                ],
                    limit=1)
                if len(records) > 0:
                    print("更新")
                    self._update_user(user, employee)
                else:
                    print("创建")
                    self._create_user(records, employee)
                self.result = True

        except BaseException:
            return False
        return self.result

    def _create_user(self, user, employee):
        # result = super(user, self).write(values)
        try:
            employee.user_id = user.sudo().create({
                'name': employee.name,
                'login': employee.userid,
                'userid': employee.userid,
            })
            print(user.name)
        except BaseException as e:
            print(e)

    def _create_user(self, cr, user, employee):
        env = api.Environment(cr, SUPERUSER_ID, {})
        object = env['res.users'].search([('dashboard_graph_model', '=', 'crm.opportunity.report')])
        employee.user_id = object.create({
            'dashboard_graph_model': None
        })

    def _update_user(self, cr, user, employee):
        env = api.Environment(cr, SUPERUSER_ID, {})
        object = env['res.users'].search([('dashboard_graph_model', '=', 'crm.opportunity.report')])
        object.update({'name': employee.name})

# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException


class Users(models.Model):
    _inherit = "res.users"

    def unbind_wecom_member(self):
        """
        解除绑定企业微信成员
        """
        self.write(
            {"is_wecom_user": False, "wecom_userid": None, "qr_code": None,}
        )
        print(self.employee_ids)
        print(self.employee_id)
        for employee in self.employee_ids:
            employee.unbind_wecom_member()

# -*- coding: utf-8 -*-

import logging

from werkzeug.urls import url_encode
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class HrEmployeePrivate(models.Model):
    _inherit = "hr.employee"

    @api.model
    def create(self, vals):
        if vals.get("user_id"):
            user = self.env["res.users"].browse(vals["user_id"])
            vals.update(self._sync_user(user, bool(vals.get("image_1920"))))
            vals["name"] = vals.get("name", user.name)
        employee = super(HrEmployeePrivate, self).create(vals)
        if employee.department_id:
            self.env["mail.channel"].sudo().search(
                [("subscription_department_ids", "in", employee.department_id.id)]
            )._subscribe_users_automatically()

        # 启动入职计划
        url = "/web#%s" % url_encode(
            {
                "action": "hrms_base.plan_wizard_action",
                "active_id": employee.id,
                "active_model": "hr.employee",
                "menu_id": self.env.ref("hrms_base.menu_hrms_root").id,
            }
        )
        employee._message_log(
            body=_(
                '<b>Congratulations!</b> May I recommend you to setup an <a href="%s">onboarding plan?</a>'
            )
            % (url)
        )
        return employee

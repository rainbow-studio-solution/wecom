# -*- coding: utf-8 -*-

from ..models.hr_employee_category import EmployeeCategory
from odoo import api, models, fields, _
from odoo.exceptions import UserError


from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException   # type: ignore

import logging

_logger = logging.getLogger(__name__)


class WizardSyncTags(models.TransientModel):
    _name = "wizard.wecom.tag"
    _description = "WeCom synchronization tag wizard"
    _order = "create_date"

    sync_tag_result = fields.Boolean(
        string="Tags synchronization result", default=False, readonly=True
    )
    times = fields.Float(string="Elapsed time (seconds)", digits=(16, 3), readonly=True)
    result = fields.Text(string="Result", readonly=True)

    def refresh_tags(self):
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }

    def action_sync_tags(self):
        """
        启动同步
        """

        (
            self.times,
            self.sync_tag_result,
            self.result,
        ) = EmployeeCategory.sync_employee_tags(self.env["hr.employee.category"])   # type: ignore

        form_view = self.env.ref("hrms_syncing.dialog_wecom_contacts_sync_tag_result")
        return {
            "name": _("WeCom tags synchronization results"),
            "view_type": "form",
            "view_mode": "form",
            "res_model": "wizard.wecom.tag",
            "res_id": self.id,  # type: ignore
            "view_id": False,
            "views": [
                [form_view.id, "form"],
            ],
            "type": "ir.actions.act_window",
            "context": {
                "form_view_ref": "hrms_syncing.dialog_wecom_contacts_sync_tag_result"
            },
            "target": "new",  # target: 打开新视图的方式，current是在本视图打开，new是弹出一个窗口打
        }

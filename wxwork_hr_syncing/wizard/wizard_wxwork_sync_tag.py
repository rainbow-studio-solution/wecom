# -*- coding: utf-8 -*-

from ..models.hr_employee_category import EmployeeCategory
from odoo import api, models, fields, _
from odoo.exceptions import UserError

# from ..models.sync_user import *

from ...wxwork_api.wx_qy_api.ErrorCode import ERRCODE, Errcode
from ...wxwork_api.wx_qy_api.AbstractApi import ApiException
from ...wxwork_api.wx_qy_api.CorpApi import CorpApi
import logging

_logger = logging.getLogger(__name__)


class WizardSyncTags(models.TransientModel):
    _name = "wizard.wxwork.tag"
    _description = "Enterprise WeChat synchronization tag wizard"
    _order = "create_date"

    sync_tag_result = fields.Boolean(
        string="Tags synchronization result", default=False, readonly=True
    )
    times = fields.Float(string="Elapsed time (seconds)", digits=(16, 3), readonly=True)
    result = fields.Text(string="Result", readonly=True)

    @api.model
    def check_api(self, corpid, secret):
        try:
            api = CorpApi(corpid, secret)
            self.env["ir.config_parameter"].sudo().set_param(
                "wxwork.contacts_access_token", api.getAccessToken()
            )
            return True

        except ApiException as ex:
            return False

    def refresh_tags(self):
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }

    def action_sync_tags(self):
        """
        启动同步
        """
        params = self.env["ir.config_parameter"].sudo()
        corpid = params.get_param("wxwork.corpid")
        secret = params.get_param("wxwork.contacts_secret")

        if not self.check_api(corpid, secret):
            raise Warning(_("Enterprise WeChat configuration is wrong, please check."))
        else:

            (
                self.times,
                self.sync_tag_result,
                self.result,
            ) = EmployeeCategory.sync_tags(self.env["hr.employee.category"])

            form_view = self.env.ref(
                "wxwork_hr_syncing.dialog_wxwork_contacts_sync_tag_result"
            )
            return {
                "name": _("Enterprise WeChat tags synchronization results"),
                "view_type": "form",
                "view_mode": "form",
                "res_model": "wizard.wxwork.tag",
                "res_id": self.id,
                "view_id": False,
                "views": [[form_view.id, "form"],],
                "type": "ir.actions.act_window",
                "context": {
                    "form_view_ref": "wxwork_hr_syncing.dialog_wxwork_contacts_sync_tag_result"
                },
                "target": "new",  # target: 打开新视图的方式，current是在本视图打开，new是弹出一个窗口打
            }

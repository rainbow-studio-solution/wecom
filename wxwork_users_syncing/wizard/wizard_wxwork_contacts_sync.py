# -*- coding: utf-8 -*-

from ...wxwork_api.wx_qy_api.ErrorCode import ERRCODE, Errcode
from ...wxwork_api.wx_qy_api.AbstractApi import ApiException
from ...wxwork_api.wx_qy_api.CorpApi import CorpApi
from odoo import api, models, fields, _
from odoo.exceptions import UserError, Warning
from ..models.sync_contacts import *


class ResConfigSettings(models.TransientModel):
    _name = "wizard.wxwork.contacts"
    _description = "Enterprise WeChat synchronization wizard"
    _order = "create_date"

    image_sync_result = fields.Boolean(
        string="Picture synchronization result",
        default=False,
        readonly=True,
        translate=True,
    )
    department_sync_result = fields.Boolean(
        string="Department synchronization result",
        default=False,
        readonly=True,
        translate=True,
    )
    employee_sync_result = fields.Boolean(
        string="Employee synchronization results",
        default=False,
        readonly=True,
        translate=True,
    )
    user_sync_result = fields.Boolean(
        string="User synchronization result",
        default=False,
        readonly=True,
        translate=True,
    )

    times = fields.Float(
        string="Elapsed time (seconds)", digits=(16, 3), readonly=True, translate=True
    )
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

    def action_sync_contacts(self):
        """
        启动同步
        """

        params = self.env["ir.config_parameter"].sudo()
        sync_hr_enabled = params.get_param("wxwork.contacts_auto_sync_hr_enabled")
        corpid = params.get_param("wxwork.corpid")
        secret = params.get_param("wxwork.contacts_secret")

        kwargs = {
            "corpid": params.get_param("wxwork.corpid"),
            "secret": params.get_param("wxwork.contacts_secret"),
            "debug": params.get_param("wxwork.debug_enabled"),
            "department_id": params.get_param("wxwork.contacts_sync_hr_department_id"),
            "sync_hr": params.get_param("wxwork.contacts_auto_sync_hr_enabled"),
            "img_path": params.get_param("wxwork.contacts_img_path"),
            "department": self.env["hr.department"],
            "employee": self.env["hr.employee"],
        }

        if not self.check_api(corpid, secret):
            raise Warning(_("Enterprise WeChat configuration is wrong, please check."))
        elif sync_hr_enabled == "False" or sync_hr_enabled is None:
            raise Warning(
                _(
                    "Tip: The current setting does not allow synchronization from enterprise WeChat to HR \n\n Please generate a user manually \n\n Please modify the related settings"
                )
            )
        else:
            self.times, statuses, self.result = SyncTask(kwargs).run()
            # self.image_sync_result = statuses["image_1920"]  # 图片同步结果
            self.department_sync_result = bool(statuses["department"])  # 部门同步结果
            # self.employee_sync_result = statuses["employee"]  # 员工同步结果

            form_view = self.env.ref(
                "wxwork_users_syncing.dialog_wxwork_contacts_sync_result"
            )
            return {
                "name": _("Update result"),
                "view_type": "form",
                "view_mode": "form",
                "res_model": "wizard.wxwork.contacts",
                "res_id": self.id,
                "view_id": False,
                "views": [[form_view.id, "form"],],
                "type": "ir.actions.act_window",
                # 'context': '{}',
                # 'context': self.env.context,
                "context": {
                    "form_view_ref": "wxwork_users_syncing.dialog_wxwork_contacts_sync_result"
                },
                "target": "new",  # target: 打开新视图的方式，current是在本视图打开，new是弹出一个窗口打开
                # 'auto_refresh': 0, #为1时在视图中添加一个刷新功能
                # 'auto_search': False, #加载默认视图后，自动搜索
                # 'multi': False, #视图中有个更多按钮，若multi设为True, 更多按钮显示在tree视图，否则显示在form视图
            }

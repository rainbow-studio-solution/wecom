# -*- coding: utf-8 -*-

from odoo.fields import Boolean
from ...wxwork_api.wx_qy_api.CorpApi import *
from ...wxwork_api.wx_qy_api.ErrorCode import *
from ...wxwork_api.helper.common import *

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError
from ..models.sync_contacts import *
import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    contacts_secret = fields.Char(
        "Contact Secret", config_parameter="wxwork.contacts_secret"
    )
    contacts_access_token = fields.Char(
        string="Contact token",
        readonly=True,
        config_parameter="wxwork.contacts_access_token",
    )
    contacts_auto_sync_hr_enabled = fields.Boolean(
        "Allow Enterprise WeChat Contacts are automatically updated to HR",
        default=True,
    )
    # contacts_sync_img_enabled = fields.Boolean(
    #     '允许同步Enterprise WeChat图片', config_parameter='wxwork.contacts_sync_img_enabled', )
    contacts_img_path = fields.Char(
        "Enterprise WeChat Picture storage path",
        config_parameter="wxwork.contacts_img_path",
    )
    contacts_sync_hr_department_id = fields.Integer(
        "Enterprise WeChat department ID to be synchronized",
        config_parameter="wxwork.contacts_sync_hr_department_id",
        default=1,
    )
    contacts_edit_enabled = fields.Boolean(
        "Allow API to edit Enterprise WeChat contacts",
        default=False,
        # readonly=True,
    )
    contacts_sync_user_enabled = fields.Boolean(
        "Allow Enterprise WeChat contacts to automatically update system accounts",
        default=False,
    )
    contacts_always_update_avatar_enabled = fields.Boolean(
        "Always update avatar", default=False,
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ir_config = self.env["ir.config_parameter"].sudo()

        contacts_auto_sync_hr_enabled = (
            True
            if ir_config.get_param("wxwork.contacts_auto_sync_hr_enabled") == "True"
            else False
        )
        contacts_edit_enabled = (
            True
            if ir_config.get_param("wxwork.contacts_edit_enabled") == "True"
            else False
        )
        contacts_sync_user_enabled = (
            True
            if ir_config.get_param("wxwork.contacts_sync_user_enabled") == "True"
            else False
        )
        contacts_always_update_avatar_enabled = (
            True
            if ir_config.get_param("wxwork.contacts_always_update_avatar_enabled")
            == "True"
            else False
        )
        res.update(
            contacts_auto_sync_hr_enabled=contacts_auto_sync_hr_enabled,
            contacts_edit_enabled=contacts_edit_enabled,
            contacts_sync_user_enabled=contacts_sync_user_enabled,
            contacts_always_update_avatar_enabled=contacts_always_update_avatar_enabled,
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ir_config = self.env["ir.config_parameter"].sudo()
        ir_config.set_param(
            "wxwork.contacts_auto_sync_hr_enabled",
            self.contacts_auto_sync_hr_enabled or "False",
        )
        ir_config.set_param(
            "wxwork.contacts_edit_enabled", self.contacts_edit_enabled or "False"
        )
        ir_config.set_param(
            "wxwork.contacts_sync_user_enabled",
            self.contacts_sync_user_enabled or "False",
        )
        ir_config.set_param(
            "wxwork.contacts_always_update_avatar_enabled",
            self.contacts_always_update_avatar_enabled or "False",
        )

    def get_contacts_access_token(self):
        ir_config = self.env["ir.config_parameter"].sudo()
        corpid = ir_config.get_param("wxwork.corpid")
        # debug = ir_config.get_param("wxwork.debug_enabled")
        if corpid == False:
            raise UserError(_("Please fill in correctly Enterprise ID."))
        elif self.contacts_secret == False:
            raise UserError(_("Please fill in the contact Secret correctly."))

        else:
            warning = {}
            try:
                api = CorpApi(corpid, self.contacts_secret)
            except ApiException as ex:
                warning = {
                    "title": _("Operation failed"),
                    "dialogClass": "bg-warning",
                    "content": _(
                        "<div>Error code: %s </br>Error description: %s </br>Error Details:</br>%s</div>"
                    )
                    % (str(ex.errCode), Errcode.getErrcode(ex.errCode), ex.errMsg),
                    "reload": "false",
                }
            else:
                warning = {
                    "title": _("Successful operation"),
                    "dialogClass": "bg-success",
                    "content": _(
                        "<div>Successfully obtained corporate WeChat contact token.</div>"
                    ),
                    "reload": "true",
                }
                self.env["ir.config_parameter"].sudo().set_param(
                    "wxwork.contacts_access_token", api.getAccessToken()
                )
            finally:
                action = {
                    "type": "ir.actions.client",
                    "tag": "dialog",
                    "params": {
                        "title": warning["title"],
                        "dialogClass": warning["dialogClass"],
                        "$content": warning["content"],
                        "size": "medium",
                        "reload": warning["reload"],
                    },
                }

                return action

    def cron_sync_contacts(self):
        """
        同步通讯录任务
        :return:
        """
        params = self.env["ir.config_parameter"].sudo()
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

        try:
            SyncTask(kwargs).run()
        except Exception as e:
            if params.get_param("wxwork.debug_enabled"):
                _logger.warning(
                    _(
                        "Task failure prompt - The task of synchronizing Enterprise WeChat contacts on a regular basis cannot be executed. The detailed reasons are as follows:%s"
                        % (e)
                    )
                )

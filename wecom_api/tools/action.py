# -*- coding: utf-8 -*-

from odoo import models, _
import logging

_logger = logging.getLogger(__name__)


class WecomApiToolsAction(models.AbstractModel):
    _name = "wecomapi.tools.action"
    _description = "Wecom API Tools - Action"

    def ApiExceptionDialog(
        self,
        ex,
        raise_exception=False,
    ):
        """
        API 错误弹框
        """
        ir_config = self.env["ir.config_parameter"].sudo()
        debug = ir_config.get_param("wecom.debug_enabled")
        error = self.env["wecom.service_api_error"].get_error_by_code(ex.errCode)

        if debug:
            _logger.warning(
                _("Wecom API error: %s, error name: %s, error message: %s")
                % (str(ex.errCode), error["name"], ex.errMsg)
            )
        if raise_exception:
            params = {
                "title": _("Failed"),
                "message": _(
                    "Error code: %s,Error description: %s,Error troubleshooting method: %s,Error Details:%s"
                )
                % (
                    str(ex.errCode),
                    str(error["name"]),
                    error["method"],
                    ex.errMsg,
                ),
                "size": "md",  # medium
            }
            action = {
                "type": "ir.actions.client",
                "tag": "wecom_api_error_dialogs",
                "params": {
                    "title": params["title"],
                    "size": params["size"],
                    "code": str(ex.errCode),
                    "description": str(error["name"]),
                    "method": str(error["method"]),
                    "details": ex.errMsg,
                },
            }
            return action

    def WecomInfoNotification(self, msg):
        """
        API 提示信息
        """
        action = {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": msg["title"],
                "type": "info",
                "message": msg["message"],
                "sticky": msg["sticky"],
            },
        }
        return action

    def WecomSuccessNotification(self, msg):
        """
        API 成功提示信息
        """
        params = {
            "title": msg["title"],
            "type": "success",
            "message": msg["message"],
            "sticky": msg["sticky"],
        }
        if "next" in msg:
            params.update({"next": msg["next"]})

        action = {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": params,
        }
        return action

    def WecomWarningNotification(self, msg):
        """
        API 警告提示信息
        """
        action = {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": msg["title"],
                "type": "warning",
                "message": msg["message"],
                "sticky": msg["sticky"],
            },
        }
        return action

    def WecomErrorNotification(self, msg):
        """
        API 错误提示信息
        """

        action = {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": msg["title"],
                "type": "error",
                "message": msg["message"],
                "sticky": msg["sticky"],
            },
        }
        return action

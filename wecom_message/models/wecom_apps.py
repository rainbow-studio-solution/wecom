# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from odoo import _, api, fields, models


class WeComApps(models.Model):
    _inherit = "wecom.apps"

    def generate_service_by_code(self, code):
        """
        根据code生成回调服务
        :param code:
        :return:
        """

        if code == "message":
            # 创建消息回调服务
            app_callback_service = (
                self.env["wecom.app_callback_service"]
                .sudo()
                .search([("app_id", "=", self.id), ("code", "=", code)])
            )
            if not app_callback_service:
                app_callback_service.create(
                    {
                        "app_id": self.id,
                        "name": _("Receive messages"),
                        "code": code,
                        "callback_url_token": "",
                        "callback_aeskey": "",
                        "description": _(
                            """
In order to enable two-way communication between self built applications and enterprise wechat, enterprises can turn on the message receiving mode in the application management background.<br/>

Enterprises that enable the message receiving mode need to provide the available message receiving server URL (HTTPS is recommended).<br/>

After the receive message mode is enabled, the messages sent by users in the application will be pushed to the enterprise background. In addition, event messages such as geographical location reporting can also be configured. When the event is triggered, the enterprise wechat will push the corresponding data to the background of the enterprise.<br/>

After receiving the message, the enterprise background can bring a new message in the response package to reply to the message request, and the enterprise wechat will push the passive reply message to the user.<br/> """
                        ),
                    }
                )
            else:
                app_callback_service.write(
                    {
                        "name": _("Receive messages"),
                        "code": code,
                        "description": _(
                            """
In order to enable two-way communication between self built applications and enterprise wechat, enterprises can turn on the message receiving mode in the application management background.<br/>

Enterprises that enable the message receiving mode need to provide the available message receiving server URL (HTTPS is recommended).<br/>

After the receive message mode is enabled, the messages sent by users in the application will be pushed to the enterprise background. In addition, event messages such as geographical location reporting can also be configured. When the event is triggered, the enterprise wechat will push the corresponding data to the background of the enterprise.<br/>

After receiving the message, the enterprise background can bring a new message in the response package to reply to the message request, and the enterprise wechat will push the passive reply message to the user.<br/> """
                        ),
                    }
                )

        super(WeComApps, self).generate_service_by_code(code)

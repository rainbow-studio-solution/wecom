# -*- coding: utf-8 -*-

import logging
import time
from datetime import datetime, timedelta
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException    # type: ignore

_logger = logging.getLogger(__name__)


class WeComApps(models.Model):
    _inherit = "wecom.apps"

    def cron_get_app_jsapi_ticket(self):
        """
        定时任务，每隔两小时更新应用的jsapi_ticket
        """
        for app in self:
            if (
                app.company_id.is_wecom_organization     # type: ignore
                and app.company_id.corpid    # type: ignore
                and app.secret   # type: ignore
            ):
                _logger.info(
                    _("Automatic tasks:Start getting JSAPI ticket for app [%s]")
                    % (app.name)     # type: ignore
                )
                if (
                    app.jsapi_ticket_expiration_time     # type: ignore
                    and app.jsapi_ticket_expiration_time > datetime.now()    # type: ignore
                ):
                    _logger.info(
                        _(
                            "Automatic tasks:JSAPI ticket for app [%s] is not expired, no need to update"
                        )
                        % (app.name)     # type: ignore
                    )
                else:
                    try:
                        wecom_api = self.env["wecom.service_api"].InitServiceApi(
                            app.company_id.corpid, app.secret    # type: ignore
                        )
                        response = wecom_api.httpCall(
                            self.env["wecom.service_api_list"].get_server_api_call(
                                "AGENT_GET_TICKET"
                            ),
                            {"type": "agent_config"},
                        )
                    except ApiException as e:
                        _logger.error(
                            _(
                                "Automatic tasks:Failed to get JSAPI ticket for app [%s], error: %s"
                            )
                            % (app.name, e)  # type: ignore
                        )
                    else:
                        if response["errcode"] == 0:
                            app.write(
                                {
                                    "jsapi_ticket": response["ticket"],
                                    "jsapi_ticket_expiration_time": datetime.now()
                                    + timedelta(seconds=response["expires_in"]),
                                }
                            )
                    _logger.info(
                        _("Automatic tasks:Successfully get JSAPI ticket for app [%s]")
                        % (app.name)     # type: ignore
                    )
            _logger.info(
                _("Automatic tasks:Start getting app [%s] ticket for company [%s]")
                % (app.name, app.company_id.name)    # type: ignore
            )

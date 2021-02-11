# -*- coding: utf-8 -*-

import logging
from odoo import api, models, _

from odoo.addons.wxwork_api.api.corp_api import CorpApi, CORP_API_TYPE


_logger = logging.getLogger(__name__)


class WxWorkMessageApi(models.AbstractModel):
    _name = "wxwork.message.api"
    _description = "Enterprise WeChat Message API"

    def _wxwork_message_send_api(self, params):
        sys_params = self.env["ir.config_parameter"].sudo()
        corpid = sys_params.get_param("wxwork.corpid")
        agentid = sys_params.get_param("wxwork.message_agentid")
        secret = sys_params.get_param("wxwork.message_secret")
        debug = sys_params.get_param("wxwork.debug_enabled")
        wxapi = CorpApi(corpid, secret)

        recipient = params["recipient"]
        msgtype = params["msgtype"]
        message = params["message"]
        options = params["options"]

        message_json = {
            "msgtype": msgtype,
            "agentid": agentid,
        }

        # 收件人
        if "touser" in recipient.keys():
            message_json["touser"] = recipient["touser"]
        if "toparty" in recipient.keys():
            message_json["toparty"] = recipient["toparty"]
        if "totag" in recipient.keys():
            message_json["totag"] = recipient["totag"]

        # 消息内容
        if "markdown" in message.keys():
            message_json["markdown"] = message["markdown"]

        # 选项
        if "safe" in options.keys():
            message_json["safe"] = options["safe"]
        if "enable_id_trans" in options.keys():
            message_json["enable_id_trans"] = options["enable_id_trans"]
        if "enable_duplicate_check" in options.keys():
            message_json["enable_duplicate_check"] = options["enable_duplicate_check"]
        if "duplicate_check_interval" in options.keys():
            message_json["duplicate_check_interval"] = options[
                "duplicate_check_interval"
            ]

        try:
            response = wxapi.httpCall(CORP_API_TYPE["MESSAGE_SEND"], message_json)
            return response
        except ApiException as e:
            _logger.exception(
                _(
                    "Send Error , error: %s",
                    (str(e.errCode), Errcode.getErrcode(e.errCode), e.errMsg),
                )
            )
            if debug:
                print(
                    _(
                        "Send Error , error: %s",
                        (str(e.errCode), Errcode.getErrcode(e.errCode), e.errMsg),
                    )
                )

    @api.model
    def _send_wxwork_message(self, recipient, msgtype, message, options):
        """
        发送一条企业微信消息 到多个人员
        """
        params = {
            "recipient": recipient,
            "msgtype": msgtype,
            "message": message,
            "options": options,
        }
        return self._wxwork_message_send_api(params)

    @api.model
    def _send_wxwork_message_batch(self, messages):
        """
        批量模式发送企业微信消息
        """
        params = {
            "recipient": messages.recipient,
            "msgtype": messages.msgtype,
            "message": messages.message,
            "options": messages.options,
        }
        return self._wxwork_message_send_api(params)

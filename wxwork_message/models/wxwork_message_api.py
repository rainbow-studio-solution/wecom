# -*- coding: utf-8 -*-

import logging
from odoo import api, models, _

from odoo.addons.wxwork_api.api.corp_api import CorpApi, CORP_API_TYPE
from odoo.addons.wxwork_api.api.abstract_api import ApiException
from odoo.addons.wxwork_api.api.error_code import Errcode

_logger = logging.getLogger(__name__)


class WxWorkMessageApi(models.AbstractModel):
    _name = "wxwork.message.api"
    _description = "Enterprise WeChat Message API"

    def _wxwork_message_send_api(self, params):
        # print(params)
        sys_params = self.env["ir.config_parameter"].sudo()
        corpid = sys_params.get_param("wxwork.corpid")
        agentid = sys_params.get_param("wxwork.message_agentid")
        secret = sys_params.get_param("wxwork.message_secret")
        debug = sys_params.get_param("wxwork.debug_enabled")
        wxapi = CorpApi(corpid, secret)

        messages = params["messages"]
        for message in messages:
            recipient = message["recipient"]
            msgtype = message["msgtype"]
            content = message["message"]
            options = message["options"]

            message_json = {
                "msgtype": msgtype,
                "agentid": agentid,
            }
            print(recipient)
            # 收件人
            if "to_user" in recipient.keys() and recipient["to_user"] != "":
                message_json["touser"] = recipient["to_user"]
            if "to_party" in recipient.keys() and recipient["to_party"] != 0:
                message_json["toparty"] = recipient["to_party"]
            if "to_tag" in recipient.keys() and recipient["to_tag"] != 0:
                message_json["totag"] = recipient["to_tag"]

            # 选项
            if "safe" in options.keys() and msgtype != "markdown":
                message_json["safe"] = options["safe"]
            if "enable_id_trans" in options.keys():
                message_json["enable_id_trans"] = options["enable_id_trans"]
            if "enable_duplicate_check" in options.keys():
                message_json["enable_duplicate_check"] = options[
                    "enable_duplicate_check"
                ]
            if "duplicate_check_interval" in options.keys():
                message_json["duplicate_check_interval"] = options[
                    "duplicate_check_interval"
                ]

            # TODO 消息内容,暂时只处理text,textcard,markdown类型
            if msgtype == "text":
                message_json["text"] = {"content": content}
            if msgtype == "textcard":
                message_json["textcard"] = {
                    "title": content,
                    "description": content,
                    "url": content,
                    "btntxt": content,
                }
            if msgtype == "markdown":
                message_json["markdown"] = {"content": content}

            print(message_json)
            try:
                response = wxapi.httpCall(CORP_API_TYPE["MESSAGE_SEND"], message_json)

                return response.get("errcode")
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
            "messages": messages,
        }
        return self._wxwork_message_send_api(params)

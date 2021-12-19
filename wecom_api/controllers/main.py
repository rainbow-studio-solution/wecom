# -*- coding: utf-8 -*-

import json
import logging
import xml.etree.cElementTree as ET
from lxml import etree
import sys
from odoo.addons.wecom_api.api.wecom_msg_crtpt import WecomMsgCrypt
from odoo import http, models, fields, _
from odoo.http import request


class StripeController(http.Controller):
    """
    """

    @http.route(
        ["/wecom_callback", "/wecom_callback/"],
        type="http",
        auth="public",
        methods=["GET", "POST"],
    )
    def WecomCallbackService(self):
        """
        企业微信回调服务
        """

    @http.route(
        ["/wecom_callback/<int:id>/<string:service>", "/wecom_callback/contacts"],
        type="http",
        auth="public",
        methods=["GET", "POST"],
        csrf=False,
    )
    def WecomCallbackService(self, service, id, **kw):
        """
        企业微信回调服务
        :param id:      公司id
        :param service: 回调服务名称 code        
        """
        company_id = request.env["res.company"].sudo().search([("id", "=", id)])
        sCorpID = company_id.corpid

        app = company_id.contacts_app_id.app_callback_service_ids.sudo().search(
            [("app_id", "=", company_id.contacts_app_id.id), ("code", "=", service)]
        )

        wxcpt = WecomMsgCrypt(app.callback_url_token, app.callback_aeskey, sCorpID)

        # 获取企业微信发送的相关参数
        sVerifyMsgSig = kw["msg_signature"]
        sVerifyTimeStamp = kw["timestamp"]
        sVerifyNonce = kw["nonce"]

        if request.httprequest.method == "GET":
            # 在企业微信后台，设置接收事件服务器时，返回一个echostr，进行验证
            sVerifyEchoStr = kw["echostr"]
            ret, msg = wxcpt.VerifyURL(
                sVerifyMsgSig, sVerifyTimeStamp, sVerifyNonce, sVerifyEchoStr
            )
            if ret != 0:
                logging.error("ERR: VerifyURL ret: " + str(ret))
                sys.exit(1)
            return msg

        if request.httprequest.method == "POST":
            # 接收企业微信事件服务器推送的消息，并进行处理
            sReqData = request.httprequest.data
            ret, msg = wxcpt.DecryptMsg(
                sReqData, sVerifyMsgSig, sVerifyTimeStamp, sVerifyNonce
            )
            if ret != 0:
                print("ERR: DecryptMsg ret: " + str(ret))
                sys.exit(1)
            # 解密成功，msg即为xml格式的明文
            # print("msg-----------", msg)
            tree = etree.fromstring(msg)  # xml解析为一个xml元素

            # xml_tree = ET.fromstring(msg)
            try:
                # event = tree.find("Event").text
                # change_type = tree.find("ChangeType").text
                # print("POST", tree)
                request.env["wecom.app.event_type"].sudo().with_context(
                    xml_tree=tree, company=company_id
                ).handle_event()  # 传递xml元素和公司
            except:
                pass

# -*- coding: utf-8 -*-

import json
import logging
import xml.etree.cElementTree as ET
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
        ["/wecom_callback/<string:service>/<int:id>", "/wecom_callback/contacts"],
        type="http",
        auth="public",
        methods=["GET", "POST"],
    )
    def WecomCallbackService(self, service, id, **kw):
        """
        企业微信回调服务
        :param service:回调服务名称 code
        :param id:      公司id
        """
        company_id = request.env["res.company"].sudo().search([("id", "=", id)])
        corpid = company_id.corpid

        if request.httprequest.method == "GET":
            app = (
                request.env["wecom.apps"]
                .sudo()
                .search([("company_id", "=", id), ("code", "=", service)])
            )

            wxcpt = WecomMsgCrypt(app.callback_url_token, app.callback_aeskey, corpid)

            msg_signature = kw["msg_signature"]
            timestamp = kw["timestamp"]
            nonce = kw["nonce"]
            echostr = kw["echostr"]

            ret, sEchoStr = wxcpt.VerifyURL(msg_signature, timestamp, nonce, echostr)
            if ret != 0:
                # print("ERR: VerifyURL ret: " + str(ret))
                logging.error("ERR: VerifyURL ret: " + str(ret))
                sys.exit(1)
            return sEchoStr

        if request.httprequest.method == "POST":
            pass

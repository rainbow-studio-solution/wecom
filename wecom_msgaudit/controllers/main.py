# -*- coding: utf-8 -*-

import werkzeug.utils
import urllib
import odoo
import sys
from odoo import http, models, fields, _
from odoo.http import request
from odoo.addons.web.controllers.main import Home, ensure_db

# from odoo.addons.wecom_api.tools.security import *


class MsgAuditHome(Home):
    @http.route(
        ["/receive_msg", "/receive_msg/"],
        type="http",
        auth="public",
        methods=["GET", "POST"],
    )
    def msgaudit_client(self, **kw):
        """
        接受服务器事件
        """
        # /msgaudit?msg_signature=9080adad44f718a22f2fb00f0e69a91319dffa13&timestamp=1638925988&nonce=1639523462&echostr=KjUoVMzhG68RW5zk%2FqUcIBK9WPGAd3omwbSWb1ZDdJ4ULJjwUP76bCAOlHRa35mUcABIji%2BmeJ23aKIwrwFf2A%3D%3D

        sToken = "dVHwFVzhNzZ"
        sEncodingAESKey = "gwE4ueDel23JRC6q1edBRBCvEJGbPCVsy0YYHWxYzEo"
        sCorpID = "wx7d3bc2004f7c66cf"

        wxcpt = (
            request.env["wecomapi.tools.security"]
            .sudo()
            .InitMsgCrypt(sToken, sEncodingAESKey, sCorpID)
        )
        print("wxcpt:", wxcpt)
        msg_signature = kw["msg_signature"]
        timestamp = kw["timestamp"]
        nonce = kw["nonce"]
        echostr = kw["echostr"]

        ret, sEchoStr = wxcpt.VerifyURL(msg_signature, timestamp, nonce, echostr)
        print("VerifyURL: ", ret, sEchoStr)
        if ret != 0:
            print("ERR: VerifyURL ret: " + str(ret))
            # sys.exit(1)

        return sEchoStr
        # HttpUtils.SetResponse(sEchoStr)

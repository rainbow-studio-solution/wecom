# -*- coding: utf-8 -*-

import json
import logging
import xml.etree.cElementTree as ET
from lxml import etree
import sys
from odoo.addons.wecom_api.api.wecom_msg_crtpt import WecomMsgCrypt
from odoo import http, models, fields, _
from odoo.http import request
from odoo.tools import ustr, consteq, frozendict, pycompat, unique, date_utils
from odoo.http import Response

_logger = logging.getLogger(__name__)


class StripeController(http.Controller):
    """ """

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
        文档URL: https://work.weixin.qq.com/api/doc/90000/90135/90930#3.2%20%E6%94%AF%E6%8C%81Http%20Post%E8%AF%B7%E6%B1%82%E6%8E%A5%E6%94%B6%E4%B8%9A%E5%8A%A1%E6%95%B0%E6%8D%AE
        """
        company_id = request.env["res.company"].sudo().search([("id", "=", id)])
        sCorpID = company_id.corpid

        callback_service = company_id.contacts_app_id.app_callback_service_ids.sudo().search(
            [
                ("app_id", "=", company_id.contacts_app_id.id),
                ("code", "=", service),
                "|",
                ("active", "=", True),
                ("active", "=", False),
            ]
        )
        if callback_service.active is False:
            _logger.info(
                _("App [%s] does not have service [%s] enabled")
                % (company_id.contacts_app_id.name, callback_service.name)
            )
            return Response("success", status=200)
        else:
            wxcpt = WecomMsgCrypt(
                callback_service.callback_url_token,
                callback_service.callback_aeskey,
                sCorpID,
            )

            # 获取企业微信发送的相关参数
            sVerifyMsgSig = kw["msg_signature"]
            sVerifyTimeStamp = kw["timestamp"]
            sVerifyNonce = kw["nonce"]

            if request.httprequest.method == "GET":
                # ^ 假设企业的接收消息的URL设置为http://api.3dept.com。
                # ^ 企业管理员在保存回调配置信息时，企业微信会发送一条验证消息到填写的URL，请求内容如下:
                # ^ 请求方式：GET
                # ^ http://api.3dept.com/?msg_signature=ASDFQWEXZCVAQFASDFASDFSS&timestamp=13500001234&nonce=123412323&echostr=ENCRYPT_STR
                # ^ 请求参数：
                # ^ msg_signature: 企业微信加密签名，msg_signature计算结合了企业填写的token、请求中的timestamp、nonce、加密的消息体。
                # ^ timestamp: 时间戳。与nonce结合使用，用于防止请求重放攻击。
                # ^ nonce: 随机数。用于保证签名不可预测。与timestamp结合使用，用于防止请求重放攻击。
                # ^ echostr: 加密的随机字符串。用于保证签名不可预测。
                sVerifyEchoStr = kw["echostr"]
                ret, msg = wxcpt.VerifyURL(
                    sVerifyMsgSig, sVerifyTimeStamp, sVerifyNonce, sVerifyEchoStr
                )
                if ret != 0:
                    logging.error("ERR: VerifyURL ret: " + str(ret))
                    sys.exit(1)
                return msg

            if request.httprequest.method == "POST":
                # ^ 假设企业的接收消息的URL设置为http://api.3dept.com。
                # ^ 当用户触发回调行为时，企业微信会发送回调消息到填写的URL，请求内容如下：
                # ^ 请求方式：POST
                # ^ 请求地址 ：http://api.3dept.com/?msg_signature=ASDFQWEXZCVAQFASDFASDFSS&timestamp=13500001234&nonce=123412323
                # ^ 请求参数：
                # ^ msg_signature: 企业微信加密签名，msg_signature计算结合了企业填写的token、请求中的timestamp、nonce、加密的消息体。
                # ^ timestamp: 时间戳。与nonce结合使用，用于防止请求重放攻击。
                # ^ nonce: 随机数。用于保证签名不可预测。与timestamp结合使用，用于防止请求重放攻击。
                # ^ ToUserName: 企业微信的CorpID，当为第三方应用回调事件时，CorpID的内容为suiteid
                # ^ AgentID: 接收的应用id，可在应用的设置页面获取。仅应用相关的回调会带该字段。
                # ^ Encrypt: 消息结构体加密后的字符串
                sReqData = request.httprequest.data
                ret, msg = wxcpt.DecryptMsg(
                    sReqData, sVerifyMsgSig, sVerifyTimeStamp, sVerifyNonce
                )
                if ret != 0:
                    logging.error("ERR: DecryptMsg ret: " + str(ret))
                    sys.exit(1)
                # 解密成功，msg即明文的xml消息结构体
                # xml_tree = etree.fromstring(msg)  # xml解析为一个xml元素
                # print("解密成功", msg)
                try:
                    return (
                        request.env["wecom.app.event_type"]
                        .sudo()
                        .with_context(xml_tree=msg, company_id=company_id)
                        .handle_event()
                    )  # 传递xml元素和公司
                except:
                    pass
                finally:
                    # ^ 正确响应企业微信本次的POST请求，企业微信将不会再次发送请求
                    # ^ ·企业微信服务器在五秒内收不到响应会断掉连接，并且重新发起请求，总共重试三次
                    # ^ ·当接收成功后，http头部返回200表示接收ok，其他错误码企业微信后台会一律当做失败并发起重试
                    # return Response("success", status=200)
                    pass

# -*- coding: utf-8 -*-

import logging
import re

import threading
from binascii import Error as binascii_error
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError

from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException

_logger = logging.getLogger(__name__)
_image_dataurl = re.compile(
    r'(data:image/[a-z]+?);base64,([a-z0-9+/\n]{3,}=*)\n*([\'"])(?: data-filename="([^"]*)")?',
    re.I,
)


class Message(models.Model):
    """
    系统通知（替换res.log通知），
    评论（OpenChatter讨论）和收到的电子邮件。
    """

    _inherit = "mail.message"

    message_to_user = fields.Char(string="To Users", help="Message recipients (users)")
    message_to_party = fields.Char(
        string="To Departments",
        help="Message recipients (departments)",
    )
    message_to_tag = fields.Char(
        string="To Tags",
        help="Message recipients (tags)",
    )

    body_html = fields.Html("Html Contents", default="", sanitize_style=True)
    body_json = fields.Text("Json Contents", default={})
    body_markdown = fields.Text("Markdown Contents", default="")
    is_wecom_message = fields.Boolean("Is WeCom Message",readonly=True)
    msgtype = fields.Selection(
        [
            ("text", "Text message"),
            ("image", "Picture message"),
            ("voice", "Voice messages"),
            ("video", "Video message"),
            ("file", "File message"),
            ("textcard", "Text card message"),
            ("news", "Graphic message"),
            ("mpnews", "Graphic message(mpnews)"),
            ("markdown", "Markdown message"),
            ("miniprogram", "Mini Program Notification Message"),
            ("taskcard", "Task card message"),
            ("template_card", "Template card message"),
        ],
        string="Message type",
        default="text",
        readonly=True
    )

    # 企业微信消息选项
    safe = fields.Selection(
        [
            ("0", "Shareable"),
            ("1", "Cannot share and content shows watermark"),
            ("2", "Only share within the company "),
        ],
        string="Secret message",
        required=True,
        default="1",
        help="Indicates whether it is a confidential message, 0 indicates that it can be shared externally, 1 indicates that it cannot be shared and the content displays watermark, 2 indicates that it can only be shared within the enterprise, and the default is 0; Note that only messages of mpnews type support the safe value of 2, and other message types do not",
    )

    enable_id_trans = fields.Boolean(
        string="Turn on id translation",
        help="Indicates whether to enable ID translation, 0 indicates no, 1 indicates yes, and 0 is the default",
        default=False,
    )
    enable_duplicate_check = fields.Boolean(
        string="Turn on duplicate message checking",
        help="Indicates whether to enable duplicate message checking. 0 indicates no, 1 indicates yes. The default is 0",
        default=False,
    )
    duplicate_check_interval = fields.Integer(
        string="Time interval for repeated message checking",
        help="Indicates whether the message check is repeated. The default is 1800s and the maximum is no more than 4 hours",
        default="1800",
    )

    state = fields.Selection(
        [
            ("sent", "Sent"),
            ("exception", "Exception"),
            ("recall", "Recall"),
        ],
        "Status",
        readonly=True,
        copy=False,
        default="sent",
    )
    failure_reason = fields.Text(
        'Failure Reason', readonly=1,)

    # ------------------------------------------------------
    # CRUD / ORM
    # ------------------------------------------------------
    

    # ------------------------------------------------------
    # 工具和发送机制
    # ------------------------------------------------------

    def send_wecom_message(self):
        """
        发送企业微信消息
        :return:
        """
        
    def recall_message(self):
        """
        撤回消息
        :return:
        """
        if self.is_wecom_message:
            # 获取公司
            company = self.env[self.model].browse(self.res_id).company_id
            if not company:
                company = self.env.company

            try:
                wecomapi = self.env["wecom.service_api"].InitServiceApi(
                    company.corpid, company.message_app_id.secret
                )
                res = wecomapi.httpCall(
                    self.env["wecom.service_api_list"].get_server_api_call(
                        "MESSAGE_RECALL"
                    ),
                    {"msgid": self.message_id},
                )
                # print(res)

            except ApiException as e:
                return self.env["wecomapi.tools.action"].ApiExceptionDialog(
                    e, raise_exception=True
                )
            else:
                if res["errcode"] == 0:
                    return self.write({"state": "recall", "message_id": None})

    def resend_message(self):
        """
        重新发送消息
        """
        if self.is_wecom_message:
            # 获取公司
            company = self.env[self.model].browse(self.res_id).company_id
            if not company:
                company = self.env.company

            wecom_userids = []
            if self.partner_ids:
                wecom_userids = [
                    p.wecom_userid
                    for p in self.partner_ids
                    if p.wecom_userid
                ]
            try:
                wecomapi = self.env["wecom.service_api"].InitServiceApi(
                    company.corpid, company.message_app_id.secret
                )
                msg = self.env["wecom.message.api"].build_message(
                    msgtype=self.msgtype,
                    touser="|".join(wecom_userids),
                    toparty=self.message_to_party,
                    totag=self.message_to_tag,
                    subject=self.subject,
                    media_id=False,
                    description=self.description,
                    author_id=self.author_id,
                    body_html=self.body_html,
                    body_json=self.body_json,
                    body_markdown=self.body_markdown,
                    safe=self.safe,
                    enable_id_trans=self.enable_id_trans,
                    enable_duplicate_check=self.enable_duplicate_check,
                    duplicate_check_interval=self.duplicate_check_interval,
                    company=company,
                )
                del msg["company"]
                res = wecomapi.httpCall(
                    self.env["wecom.service_api_list"].get_server_api_call(
                        "MESSAGE_SEND"
                    ),
                    msg,
                )

            except ApiException as e:
                return self.env["wecomapi.tools.action"].ApiExceptionDialog(
                    e, raise_exception=True
                )
            else:
                if res["errcode"] == 0:
                    return self.write({"state": "sent", "message_id": res["msgid"]})
        
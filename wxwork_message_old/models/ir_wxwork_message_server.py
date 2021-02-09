# -*- coding: utf-8 -*-
from email.message import EmailMessage
from email.utils import make_msgid
import datetime
import email
import email.policy
import logging
import re
import smtplib
from socket import gaierror, timeout
from ssl import SSLError
import sys
import threading

import html2text
import idna
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from odoo.tools import ustr, pycompat, formataddr


class IrWxworkMessageServer(models.Model):
    _name = "ir.wxwork_message_server"
    _description = "Mail Server"
    _order = "sequence"

    @api.model
    def _get_default_from_address(self):
        """
        从地址计算默认值。 

        当没有收到其他消息时，用于“发件人来自”地址。 

        :return str/None:
            结合配置参数  ``mail.default.from`` and
            ``mail.catchall.domain`` 生成默认的发件人地址。 

            如果未定义其中一些参数，则默认为 
            ``--email-from`` CLI/config parameter.
        """
        get_param = self.env["ir.config_parameter"].sudo().get_param
        domain = get_param("mail.catchall.domain")
        email_from = get_param("mail.default.from")
        if email_from and domain:
            return "%s@%s" % (email_from, domain)
        return tools.config.get("email_from")

    def build_message(
        self,
        email_from,
        email_to,
        subject,
        body,
        email_cc=None,
        email_bcc=None,
        reply_to=False,
        attachments=None,
        message_id=None,
        references=None,
        object_id=False,
        subtype="plain",
        headers=None,
        body_alternative=None,
        subtype_alternative="plain",
    ):
        """
        根据传递的关键字参数构造一个 "Message" 对象，并将其返回。 
        :param string email_from: 发件人企业微信id
        :param list email_to: 收件人企业微信id（以逗号分隔） 
        :param string subject: 企业微信消息主题 （无需预先编码/引用） 
        :param string body: 企业微信消息正文，其类型为``subtype`` （默认为纯文本）。
                            如果使用html子类型，则除非通过明确的``body_alternative``版本，否则消息将自动转换为纯文本并以multipart / alternative包装。 
        :param string body_alternative: 可选的替代主体，在``subtype_alternative``中指定的类型 
        :param string reply_to: Reply-To标头的可选值 
        :param string object_id: 可选的跟踪标识符，将包含在message-id中以识别答复。 对象ID的建议格式为"res_id-model"，例如 "12345-crm.lead"。 
        :param string subtype: 文本主体的可选mime子类型（通常为 'plain' 或 'html'），必须与``body``参数的格式匹配。 默认值为'plain'，使邮件的内容部分为“文本/普通”。 
        :param string subtype_alternative: 可选的``body_alternative``的mime子类型（通常是'plain' 或 'html'）。 默认值为 'plain'.
        :param list attachments: （文件名，文件内容）对的列表，其中文件内容是包含附件字节的字符串 
        :param list email_cc:用于CC头字符串值的可选列表（用逗号接合）
        :param list email_bcc: BCC标头的字符串值的可选列表（用逗号接合）
        :param dict headers: 要在外发邮件上设置的标头的可选映射（可以覆盖其他标头，包括“主题”，“回复至”，“邮件ID”等） 
        :rtype: email.message.EmailMessage
        :return: the new RFC2822 email message
        """
        email_from = email_from or self._get_default_from_address()
        assert email_from, (
            "You must either provide a sender address explicitly or configure "
            "using the combintion of `mail.catchall.domain` and `mail.default.from` "
            "ICPs, in the server configuration file or with the "
            "--email-from startup parameter."
        )
        headers = headers or {}  # need valid dict later
        email_cc = email_cc or []
        email_bcc = email_bcc or []
        body = body or u""

        msg = EmailMessage(policy=email.policy.SMTP)
        msg.set_charset("utf-8")

        if not message_id:
            if object_id:
                message_id = tools.generate_tracking_message_id(object_id)
            else:
                message_id = make_msgid()
        msg["Message-Id"] = message_id
        if references:
            msg["references"] = references
        msg["Subject"] = subject
        msg["From"] = email_from
        del msg["Reply-To"]
        msg["Reply-To"] = reply_to or email_from
        msg["To"] = email_to
        if email_cc:
            msg["Cc"] = email_cc
        if email_bcc:
            msg["Bcc"] = email_bcc
        msg["Date"] = datetime.datetime.utcnow()
        for key, value in headers.items():
            msg[pycompat.to_text(ustr(key))] = value

        email_body = ustr(body)
        if subtype == "html" and not body_alternative:
            msg.add_alternative(
                html2text.html2text(email_body), subtype="plain", charset="utf-8"
            )
            msg.add_alternative(email_body, subtype=subtype, charset="utf-8")
        elif body_alternative:
            msg.add_alternative(
                ustr(body_alternative), subtype=subtype_alternative, charset="utf-8"
            )
            msg.add_alternative(email_body, subtype=subtype, charset="utf-8")
        else:
            msg.set_content(email_body, subtype=subtype, charset="utf-8")

        if attachments:
            for (fname, fcontent, mime) in attachments:
                maintype, subtype = (
                    mime.split("/")
                    if mime and "/" in mime
                    else ("application", "octet-stream")
                )
                msg.add_attachment(fcontent, maintype, subtype, filename=fname)
        return msg

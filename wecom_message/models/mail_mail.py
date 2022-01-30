# -*- coding: utf-8 -*-

import logging
import ast
import base64
import datetime
import logging
import psycopg2
import smtplib
import re
from odoo import _, api, fields, models
from odoo import tools
from odoo.addons.base.models.ir_mail_server import MailDeliveryException
from odoo.exceptions import UserError, Warning
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException

_logger = logging.getLogger(__name__)


class MailMail(models.Model):
    _inherit = "mail.mail"

    media_id = fields.Many2one(
        string="Media file id",
        comodel_name="wecom.material",
        help="Media file ID, which can be obtained by calling the upload temporary material interface",
    )
    body_html = fields.Text("Html Body", translate=True, sanitize=False)
    body_json = fields.Text("Json Body", translate=True,)
    body_markdown = fields.Text("Markdown Body", translate=True)
    description = fields.Char(
        "Short description",
        compute="_compute_description",
        help="Message description: either the subject, or the beginning of the body",
    )

    message_to_user = fields.Char(string="To Users", help="Message recipients (users)")
    message_to_party = fields.Char(
        string="To Departments", help="Message recipients (departments)",
    )
    message_to_tag = fields.Char(string="To Tags", help="Message recipients (tags)",)
    use_templates = fields.Boolean("Is template message", default=False)
    templates_id = fields.Many2one("wecom.message.template", string="Message template")
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

    # 消息状态
    # message_id = fields.Char(
    #     "Message-Id",
    #     help="Used to recall application messages",
    #     # index=True,
    #     readonly=1,
    #     copy=False,
    # )

    state = fields.Selection(selection_add=[("wecom_exception", "Send exception")])

    def send_wecom_message(
        self, auto_commit=False, raise_exception=False, company=None,
    ):
        """ 
        立即发送所选电子邮件，忽略其当前状态（已发送的邮件不应被传递，除非它们实际上应该被重新发送）。
        成功发送的电子邮件被标记为“已发送”，未能发送的电子邮件被标记为“异常”，相应的错误邮件被输出到服务器日志中。
            :param bool auto_commit: 是否在发送每封邮件后强制提交邮件状态（仅用于调度程序处理）；
                                    在正常事务中不应为True（默认值:False）
            :param bool raise_exception: 如果电子邮件发送过程失败，是否引发异常
            :param bool is_wecom_message: 标识是企业微信消息
            :param company: 公司
            :return: True
        """
        if not company:
            company = self.env.company
        for batch_ids in self.ids:
            try:
                WeComMessageApi = self.env["wecom.message.api"].get_message_api(company)
            except ApiException as exc:
                if raise_exception:
                    return self.env["wecomapi.tools.action"].ApiExceptionDialog(
                        exc, raise_exception=True
                    )
                else:
                    batch = self.browse(batch_ids)
                    batch.write(
                        {"state": "wecom_exception", "failure_reason": exc.errMsg}
                    )
            else:
                self.browse(batch_ids)._send_wecom_message(
                    auto_commit=auto_commit,
                    raise_exception=raise_exception,
                    company=company,
                    WeComMessageApi=WeComMessageApi,
                )
            finally:
                pass

    def _send_wecom_message(
        self,
        auto_commit=False,
        raise_exception=False,
        company=None,
        WeComMessageApi=None,
    ):
        """
        发送企业微信消息
        :param bool auto_commit: 发送每封邮件后是否强制提交邮件状态（仅用于调度程序处理）；
                 在正常发送绝对不能为True（默认值：False）
        :param bool raise_exception: 如果电子邮件发送过程失败，是否引发异常
        :return: True
        """
        if not company:
            company = self.env.company
        ApiObj = self.env["wecom.message.api"]
        for mail_id in self.ids:
            mail = None
            try:
                mail = self.browse(mail_id)
                if mail.state != "outgoing":
                    if mail.state != "wecom_exception" and mail.auto_delete:
                        mail.sudo().unlink()
                    continue

                # email_list = []

                msg = ApiObj.build_message(
                    msgtype=mail.msgtype,
                    touser=mail.message_to_user,
                    toparty=mail.message_to_party,
                    totag=mail.message_to_tag,
                    subject=mail.subject,
                    media_id=mail.media_id,
                    description=mail.description,
                    author_id=mail.author_id,
                    body_html=mail.body_html,
                    body_json=mail.body_json,
                    body_markdown=mail.body_markdown,
                    safe=mail.safe,
                    enable_id_trans=mail.enable_id_trans,
                    enable_duplicate_check=mail.enable_duplicate_check,
                    duplicate_check_interval=mail.duplicate_check_interval,
                    company=company,
                )
                del msg["company"]  # 删除message中的 company
                res = WeComMessageApi.httpCall(
                    self.env["wecom.service_api_list"].get_server_api_call(
                        "MESSAGE_SEND"
                    ),
                    msg,
                )
            except ApiException as exc:
                error = self.env["wecom.service_api_error"].get_error_by_code(
                    exc.errCode
                )
                self.write(
                    {
                        "state": "wecom_exception",
                        "failure_reason": "%s %s" % (str(error["code"]), error["name"]),
                    }
                )
                if raise_exception:
                    return self.env["wecomapi.tools.action"].ApiExceptionDialog(
                        exc, raise_exception
                    )
            else:
                # 如果try中的程序执行过程中没有发生错误，继续执行else中的程序；
                mail.write(
                    {"state": "outgoing", "message_id": res["msgid"],}
                )
            if auto_commit is True:
                self._cr.commit()
        return True

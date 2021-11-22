# -*- coding: utf-8 -*-

import logging
from collections import defaultdict
from odoo import api, fields, models, tools, _
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException

_logger = logging.getLogger(__name__)


class WecomMessage(models.Model):
    _name = "wecom.message"
    _description = "Wecom Message"
    _order = "id desc"
    _rec_name = "record_name"

    @api.model
    def default_get(self, fields):
        res = super(WxworkMessage, self).default_get(fields)
        missing_author = "author_id" in fields and "author_id" not in res
        missing_email_from = "sender" in fields and "sender" not in res
        if missing_author or missing_email_from:
            author_id, sender = self.env["mail.thread"]._message_compute_author(
                res.get("author_id"), res.get("sender"), raise_exception=False
            )
            if missing_email_from:
                res["sender"] = sender
            if missing_author:
                res["author_id"] = author_id
        return res

    # 企业微信消息内容
    subject = fields.Char("Subject")
    date = fields.Datetime("Date", default=fields.Datetime.now)
    media_id = fields.Many2one(
        string="Media file id",
        comodel_name="wecom.material",
        help="Media file ID, which can be obtained by calling the upload temporary material interface",
    )
    body_html = fields.Html("Html Body", translate=True, sanitize=False)
    body_not_html = fields.Text("Json Body", translate=True)
    body = fields.Html("Contents", default="", sanitize_style=True)
    description = fields.Char(
        "Short description",
        compute="_compute_description",
        help="Message description: either the subject, or the beginning of the body",
    )
    message_to_all = fields.Boolean("To all members")
    message_to_user = fields.Char(string="To Users", help="Message recipients (users)")
    message_to_party = fields.Char(
        string="To Departments",
        help="Message recipients (departments)",
    )
    message_to_tag = fields.Char(
        string="To Tags",
        help="Message recipients (tags)",
    )
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
    state = fields.Selection(
        [
            ("sent", "Sent"),
            ("exception", "Delivery Failed"),
            ("cancel", "Cancelled"),
        ],
        string="State",
    )
    failure_reason = fields.Text(
        "Failure Reason",
        readonly=1,
        help="Failure reason. This is usually the exception thrown by the wecom api, stored to ease the debugging of message issues.",
    )
    scheduled_date = fields.Char(
        "Scheduled Send Date",
        help="If set, the queue manager will send the message after the date. If not set, the message will be send as soon as possible.",
    )

    # 关联
    model = fields.Char("Related Document Model", index=True)
    res_id = fields.Many2oneReference(
        "Related Document ID", index=True, model_field="model"
    )
    record_name = fields.Char(
        "Message Record Name", help="Name get of the related document."
    )

    # 特性
    message_type = fields.Selection(
        [
            ("email", "Email Message"),
            ("comment", "Comment Message"),
            ("notification", "System Notification Message"),
            ("user_notification", "User Specific Notification Message"),
        ],
        "Type",
        required=True,
        default="email",
        help="Message type: email for email message, notification for system "
        "message, comment for other messages such as user replies",
    )
    subtype_id = fields.Many2one(
        "mail.message.subtype", "Subtype", ondelete="set null", index=True
    )  # 子类型
    mail_activity_type_id = fields.Many2one(
        "mail.activity.type", "Mail Activity Type", index=True, ondelete="set null"
    )
    is_internal = fields.Boolean(
        "Employee Only",
        help="Hide to public / portal users, independently from subtype configuration.",
    )  # 内部消息

    # 来源
    # origin
    sender = fields.Char(
        "Sender",
    )
    meaasge_from = fields.Char(
        "From",
        help="Email address of the sender. This field is set when no matching partner is found and replaces the author_id field in the chatter.",
    )
    author_id = fields.Many2one(
        "res.partner",
        "Author",
        index=True,
        ondelete="set null",
        help="Author of the message. If not set, email_from may hold an email address that did not match any partner.",
    )
    author_avatar = fields.Binary(
        "Author's avatar",
        related="author_id.image_128",
        depends=["author_id"],
        readonly=False,
    )
    # 收件人：包括非活动合作伙伴（他们可能在邮件发送后已存档，但在关系中应保持可见）
    partner_ids = fields.Many2many(
        "res.partner", string="Recipients", context={"active_test": False}
    )
    # 具有通知的合作伙伴列表。警告：由于notif gc cron，列表可能会随时间而更改。
    # 主要用于测试
    # notified_partner_ids = fields.Many2many(
    #     "res.partner",
    #     "mail_message_res_partner_needaction_rel",
    #     string="Partners with Need Action",
    #     context={"active_test": False},
    #     depends=["notification_ids"],
    # )
    needaction = fields.Boolean(
        "Need Action",
        # compute="_get_needaction",
        search="_search_needaction",
        help="Need Action",
    )

    msgid = fields.Char(
        "Message-Id",
        help="Used to recall application messages",
        # index=True,
        readonly=1,
        copy=False,
    )

    def _compute_description(self):
        for message in self:
            if message.subject:
                message.description = message.subject
            else:
                plaintext_ct = (
                    "" if not message.body else tools.html2plaintext(message.body)
                )
                message.description = plaintext_ct[:30] + "%s" % (
                    " [...]" if len(plaintext_ct) >= 30 else ""
                )

    # ------------------------------------------------------
    # 消息格式、工具和发送机制
    # mail_mail formatting, tools and send mechanism
    # ------------------------------------------------------
    def _send_prepare_body(self):
        self.ensure_one()
        return self.body_html or ""

    def _send_prepare_values(self, partner=None):
        self.ensure_one()

    def _split_messages(self):
        """
        拆分消息
        """
        groups = defaultdict(list)

        for record_ids in groups.items():
            for message_batch in tools.split_every(record_ids):
                yield message_batch

    def send(
        self,
        auto_commit=False,
        raise_exception=False,
        company=None,
    ):
        """
        立即发送选定的企业微信消息，而忽略它们的当前状态（除非已被重新发送，否则不应该传递已经发送的企业微信消息）。
        成功发送的消息被标记为“已发送”，未发送成功的消息被标记为“例外”，并且相应的错误邮件将输出到服务器日志中。

        :param bool auto_commit: 在发送每条消息后是否强制提交消息状态（仅用于调度程序处理）；
            在正常传递中，永远不应该为True（默认值：False）
        :param bool raise_exception: 如果电子邮件发送过程失败，将引发异常
        :param bool is_wecom_message: 标识是企业微信消息
        :param company: 公司
        :return: True
        """
        if not company:
            company = self.env.company
        # try:
        #     wxapi = self.env["wecom.service_api"].init_api(
        #         self.company_id, "message_secret ", "message"
        #     )
        # except ApiException as exc:
        #     error = self.env["wecom.service_api_error"].get_error_by_code(exc.errCode)
        #     self.write(
        #         {
        #             "state": "exception",
        #             "failure_reason": "%s %s" % (str(error["code"]), error["name"]),
        #         }
        #     )
        #     if raise_exception:
        #         return self.env["wecomapi.tools.action"].ApiExceptionDialog(
        #             exc, raise_exception
        #         )
        # else:
        #     # 如果try中的程序执行过程中没有发生错误，继续执行else中的程序；
        self.single_send(
            auto_commit=auto_commit,
            raise_exception=raise_exception,
            company=company,
        )
        _logger.info("Sent batch %s messages via wecom ", len(self))

    def batch_send(self):
        """
        批量发送企业微信消息
        """

    def send(
        self,
        auto_commit=False,
        raise_exception=False,
        company=None,
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
        IrWxWorkMessageApi = self.env["wecom.message.api"]
        for message_id in self.ids:
            success_pids = []
            failure_type = None
            message = None

            message = self.browse(message_id)
            msg = IrWxWorkMessageApi.build_message(
                msgtype=message.msgtype,
                toall=message.message_to_all,
                touser=message.message_to_user,
                toparty=message.message_to_party,
                totag=message.message_to_tag,
                subject=message.subject,
                media_id=message.media_id,
                description=message.description,
                author_id=message.author_id,
                body_html=message.body_html,
                body_json=message.body_not_html,
                safe=message.safe,
                enable_id_trans=message.enable_id_trans,
                enable_duplicate_check=message.enable_duplicate_check,
                duplicate_check_interval=message.duplicate_check_interval,
                company=company,
            )
            try:
                res = IrWxWorkMessageApi.send_by_api(msg)
            except ApiException as exc:
                error = self.env["wecom.service_api_error"].get_error_by_code(
                    exc.errCode
                )
                self.write(
                    {
                        "state": "exception",
                        "failure_reason": "%s %s" % (str(error["code"]), error["name"]),
                    }
                )
                if raise_exception:
                    return self.env["wecomapi.tools.action"].ApiExceptionDialog(
                        exc, raise_exception
                    )
            else:
                # 如果try中的程序执行过程中没有发生错误，继续执行else中的程序；
                message.write(
                    {
                        "state": "sent",
                        "msgid": res["msgid"],
                    }
                )
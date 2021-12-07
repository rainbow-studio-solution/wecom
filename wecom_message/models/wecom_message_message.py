# -*- coding: utf-8 -*-

import logging
from collections import defaultdict
from odoo import api, fields, models, tools, _
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException

_logger = logging.getLogger(__name__)


class WecomMessageMessage(models.Model):
    """
    企业微信消息模型：系统通知（替换res.log通知），
    评论（OpenChatter讨论）和收到的电子邮件。
    """

    _name = "wecom.message.message"
    _description = "Wecom Message"
    _order = "id desc"
    _rec_name = "record_name"

    @api.model
    def default_get(self, fields):
        res = super(WecomMessageMessage, self).default_get(fields)
        missing_author = "author_id" in fields and "author_id" not in res
        missing_email_from = "meaasge_from" in fields and "meaasge_from" not in res
        if missing_author or missing_email_from:
            author_id, meaasge_from = self.env["mail.thread"]._message_compute_author(
                res.get("author_id"), res.get("meaasge_from"), raise_exception=False
            )
            if missing_email_from:
                res["meaasge_from"] = meaasge_from
            if missing_author:
                res["author_id"] = author_id

        return res

    # def _default_name(self):
    #     return "%s" % (self.subject)

    # 企业微信消息内容
    subject = fields.Char("Subject")
    date = fields.Datetime("Date", default=fields.Datetime.now)
    media_id = fields.Many2one(
        string="Media file id",
        comodel_name="wecom.material",
        help="Media file ID, which can be obtained by calling the upload temporary material interface",
    )
    body_html = fields.Text("Html Body", translate=True, sanitize=False)
    body_json = fields.Text(
        "Json Body",
        translate=True,
    )
    body_markdown = fields.Text("Markdown Body", translate=True)
    description = fields.Char(
        "Short description",
        compute="_compute_description",
        help="Message description: either the subject, or the beginning of the body",
    )

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
    # API

    msgid = fields.Char(
        "Message-Id",
        help="Used to recall application messages",
        # index=True,
        readonly=1,
        copy=False,
    )
    state = fields.Selection(
        [
            ("sent", "Sent"),
            ("exception", "Send exception"),
            ("cancel", "Cancelled"),
        ],
        string="State",
    )
    auto_delete = fields.Boolean(
        "Auto Delete",
        help="This option permanently removes any track of message after it's been sent, in order to preserve storage space of your Odoo database.",
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
    # mail_activity_type_id = fields.Many2one(
    #     "mail.activity.type", "Mail Activity Type", index=True, ondelete="set null"
    # )
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
        help="Wecom user id of the sender. This field is set when no matching partner is found and replaces the author_id field in the chatter.",
    )
    author_id = fields.Many2one(
        "res.partner",
        "Author",
        index=True,
        ondelete="set null",
        help="Author of the message. If not set, meaasge_from may hold an message wecom user id that did not match any partner.",
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
    #     "wecom_message_message_res_partner_needaction_rel",
    #     "message_message_id",
    #     string="Partners with Need Action",
    #     context={"active_test": False},
    #     depends=["notification_ids"],
    # )

    channel_ids = fields.Many2many(
        "mail.channel", "wecom_message_message_mail_channel_rel", string="Channels"
    )
    # notification_ids = fields.One2many(
    #     "wecom.message.notification",
    #     "message_message_id",
    #     "Notifications",
    #     auto_join=True,
    #     copy=False,
    #     depends=["notified_partner_ids"],
    # )
    needaction = fields.Boolean(
        "Need Action",
        # compute="_get_needaction",
        search="_search_needaction",
        help="Need Action",
    )

    def _compute_description(self):
        for message in self:
            if message.subject:
                message.description = message.subject
            else:
                plaintext_ct = (
                    ""
                    if not message.body_html
                    else tools.html2plaintext(message.body_html)
                )
                message.description = plaintext_ct[:30] + "%s" % (
                    " [...]" if len(plaintext_ct) >= 30 else ""
                )

    # ------------------------------------------------------
    # CRUD / ORM
    # ------------------------------------------------------
    @api.model_create_multi
    def create(self, values_list):
        # tracking_values_list = []
        for values in values_list:
            if (
                "record_name" not in values
                and "default_record_name" not in self.env.context
            ):
                values["record_name"] = self._get_record_name(values)
        messages = super(WecomMessageMessage, self).create(values_list)
        return messages

    # ------------------------------------------------------
    # TOOLS
    # ------------------------------------------------------
    def _get_record_name(self, values):
        """Return the related document name, using name_get. It is done using
        SUPERUSER_ID, to be sure to have the record name correctly stored."""
        model = values.get("model", self.env.context.get("default_model"))
        res_id = values.get("res_id", self.env.context.get("default_res_id"))
        if not model or not res_id or model not in self.env:
            return False
        return self.env[model].sudo().browse(res_id).display_name

    # ------------------------------------------------------
    # 消息格式、工具和发送机制
    # mail_mail formatting, tools and send mechanism
    # ------------------------------------------------------
    def _send_prepare_body_html(self):
        self.ensure_one()
        return self.body_html or ""

    def _send_prepare_body_json(self):
        self.ensure_one()
        return self.body_json or ""

    def _send_prepare_body_markdown(self):
        self.ensure_one()
        return self.body_markdown or ""

    def _send_prepare_values(self, partner=None):
        """
        根据合作伙伴的不同，返回特定电子邮件值的字典，或返回mail.email_to给定的整个收件人的通用字典。

        :param Model partner: 特定收件人合作伙伴
        """
        self.ensure_one()
        body_html = self._send_prepare_body_html()
        body_json = self._send_prepare_body_json()
        body_markdown = self._send_prepare_body_markdown()
        # body_alternative = tools.html2plaintext(body)
        # if partner:
        #     email_to = [
        #         tools.formataddr((partner.name or "False", partner.email or "False"))
        #     ]
        # else:
        #     email_to = tools.email_split_and_format(self.email_to)
        res = {
            "body_html": body_html,
            "body_json": body_json,
            "body_markdown": body_markdown,
            # "body_alternative": body_alternative,
            # "email_to": email_to,
        }
        return res

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

        for batch_ids in self.ids:
            try:
                WeComMessageApi = self.env["wecom.message.api"].get_message_api(company)
            except ApiException as exc:
                if raise_exception:
                    return self.env["wecom.tools"].ApiExceptionDialog(exc)
                else:
                    batch = self.browse(batch_ids)
                    batch.write({"state": "exception", "failure_reason": exc.errMsg})
            else:
                self.browse(batch_ids)._send(
                    auto_commit=auto_commit,
                    raise_exception=raise_exception,
                    company=company,
                    WeComMessageApi=WeComMessageApi,
                )
            finally:
                pass

    def _send(
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
        for message_id in self.ids:
            message = None
            try:
                message = self.browse(message_id)
                msg = ApiObj.build_message(
                    msgtype=message.msgtype,
                    touser=message.message_to_user,
                    toparty=message.message_to_party,
                    totag=message.message_to_tag,
                    subject=message.subject,
                    media_id=message.media_id,
                    description=message.description,
                    author_id=message.author_id,
                    body_html=message.body_html,
                    body_json=message.body_json,
                    body_markdown=message.body_markdown,
                    safe=message.safe,
                    enable_id_trans=message.enable_id_trans,
                    enable_duplicate_check=message.enable_duplicate_check,
                    duplicate_check_interval=message.duplicate_check_interval,
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
            if auto_commit is True:
                self._cr.commit()
        return True

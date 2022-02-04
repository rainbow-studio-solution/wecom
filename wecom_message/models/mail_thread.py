# -*- coding: utf-8 -*-


import logging
from odoo import _, api, exceptions, fields, models, tools, registry, SUPERUSER_ID
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException

_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    """
    邮件线程模型被任何需要作为讨论主题的模型所继承，消息可以附加在讨论主题上。
    公共方法的前缀是``message```以避免与将从此类继承的模型的方法发生名称冲突。


    ``mail.thread``定义用于处理和显示通信历史记录的字段。
    ``mail.thread``还管理继承类的跟随者。所有功能和预期行为都由管理 mail.thread.
    Widgets是为7.0及以下版本的Odoo设计的。

    实现任何方法都不需要继承类，因为默认实现适用于任何模型。
    但是，在处理传入电子邮件时，通常至少重写``message_new``和``message_update``方法（调用``super``），以便在创建和更新线程时添加特定于模型的行为。

    选项:
        - _mail_flat_thread:
            如果设置为True，则所有没有parent_id的邮件将自动附加到发布在源上的第一条邮件。
            如果设置为False，则使用线程显示Chatter，并且不会自动设置parent_id。

    MailThread特性可以通过上下文键进行某种程度的控制 :

     - ``mail_create_nosubscribe``: 在创建或消息发布时，不要向记录线程订阅uid
     - ``mail_create_nolog``: 在创建时，不要记录自动的'<Document>created'消息
     - ``mail_notrack``: 在创建和写入时，不要执行值跟踪创建消息
     - ``tracking_disable``: 在创建和写入时，不执行邮件线程功能（自动订阅、跟踪、发布…）
     - ``mail_notify_force_send``: 如果要发送的电子邮件通知少于50个，请直接发送，而不是使用队列；默认情况下为True
    """

    _inherit = "mail.thread"

    # ------------------------------------------------------
    # 消息推送API
    # MESSAGE POST API
    # ------------------------------------------------------

    def _check_is_wecom_message(self, message_values):
        """
        判断是否是企微消息
        """
        model = message_values["model"]
        res_id = message_values["res_id"]
        fields = self.env[model]._fields.keys()
        if "is_wecom_user" in fields:
            return self.env[model].browse(res_id).is_wecom_user
        else:
            return False

    @api.returns("mail.message", lambda value: value.id)
    def message_post(
        self,
        *,
        body="",
        subject=None,
        message_type="notification",
        email_from=None,
        author_id=None,
        parent_id=False,
        subtype_xmlid=None,
        subtype_id=False,
        partner_ids=None,
        channel_ids=None,
        attachments=None,
        attachment_ids=None,
        add_sign=True,
        record_name=False,
        **kwargs
    ):
        """
        在现有线程中发布新邮件，返回新的 mail.message ID。
        :param str body: 邮件的正文，通常是经过清理的原始 HTML
        :param str subject: 邮件的主题
        :param str message_type: 请参阅mail_message.message_type 字段。可以是user_notification以外的任何东西，保留给message_notify
        :param int parent_id: handle thread formation
        :param int subtype_id: subtype_id 的消息，主要采用前关注者机制
        :param list(int) partner_ids: 通知partner_ids
        :param list(int) channel_ids: 通知channel_ids
        :param list(tuple(str,str), tuple(str,str, dict) or int) attachments : 表单中的附件元组列表
            ``(name,content)`` 或 ``(name,content, info)``, 其中内容未进行 base64 编码
        :param list id attachment_ids: 要链接到此邮件的现有附件列表
            -Should only be setted by chatter 只能通过聊天chatter来设置
            -附加到 mail.compose.message(0) 的附加对象将附加到相关文档中。
        额外的关键字参数将用作新 mail.message 记录的默认列值。
        :return int: 新创建的mail.message的 ID
        """

        self.ensure_one()  # 应始终张贴在记录上，使用message_notify如果没有记录拆分消息附加值通知附加值
        msg_kwargs = dict(
            (key, val)
            for key, val in kwargs.items()
            if key in self.env["mail.message"]._fields
        )
        notif_kwargs = dict(
            (key, val) for key, val in kwargs.items() if key not in msg_kwargs
        )

        if (
            self._name == "mail.thread"
            or not self.id
            or message_type == "user_notification"
        ):
            raise ValueError(
                "message_post should only be call to post message on record. Use message_notify instead"
            )

        if "model" in msg_kwargs or "res_id" in msg_kwargs:
            raise ValueError(
                "message_post doesn't support model and res_id parameters anymore. Please call message_post on record."
            )
        if "subtype" in kwargs:
            raise ValueError(
                "message_post doesn't support subtype parameter anymore. Please give a valid subtype_id or subtype_xmlid value instead."
            )

        self = self._fallback_lang()  # 立即将lang添加到上下文中，因为它将在后面的各种流中使用。

        # 显式访问权限检查，因为display_name计算为 sudo。
        self.check_access_rights("read")
        self.check_access_rule("read")
        record_name = record_name or self.display_name

        partner_ids = set(partner_ids or [])
        channel_ids = set(channel_ids or [])

        if any(not isinstance(pc_id, int) for pc_id in partner_ids | channel_ids):
            raise ValueError(
                "message_post partner_ids and channel_ids must be integer list, not commands"
            )

        # 查找邮件的作者
        author_id, email_from = self._message_compute_author(
            author_id, email_from, raise_exception=True
        )

        if subtype_xmlid:
            subtype_id = self.env["ir.model.data"].xmlid_to_res_id(subtype_xmlid)
        if not subtype_id:
            subtype_id = self.env["ir.model.data"].xmlid_to_res_id("mail.mt_note")

        # 如果要求，自动订阅收件人
        if self._context.get("mail_post_autofollow") and partner_ids:
            self.message_subscribe(list(partner_ids))

        MailMessage_sudo = self.env["mail.message"].sudo()
        if self._mail_flat_thread and not parent_id:
            parent_message = MailMessage_sudo.search(
                [
                    ("res_id", "=", self.id),
                    ("model", "=", self._name),
                    ("message_type", "!=", "user_notification"),
                ],
                order="id ASC",
                limit=1,
            )
            # parent_message searched in sudo for performance, only used for id.
            # 在sudo中搜索parent_message以获取性能，仅用于id。

            # Note that with sudo we will match message with internal subtypes.
            # 注意，对于sudo，我们将消息与内部子类型匹配。
            parent_id = parent_message.id if parent_message else False
        elif parent_id:
            old_parent_id = parent_id
            parent_message = MailMessage_sudo.search(
                [("id", "=", parent_id), ("parent_id", "!=", False)], limit=1
            )
            # avoid loops when finding ancestors 查找祖先时避免循环
            processed_list = []
            if parent_message:
                new_parent_id = parent_message.parent_id and parent_message.parent_id.id
                while new_parent_id and new_parent_id not in processed_list:
                    processed_list.append(new_parent_id)
                    parent_message = parent_message.parent_id
                parent_id = parent_message.id

        values = dict(msg_kwargs)
        values.update(
            {
                "author_id": author_id,
                "email_from": email_from,
                "model": self._name,
                "res_id": self.id,
                "body": body,
                "subject": subject or False,
                "message_type": message_type,
                "parent_id": parent_id,
                "subtype_id": subtype_id,
                "partner_ids": partner_ids,
                "channel_ids": channel_ids,
                "add_sign": add_sign,
                "record_name": record_name,
            }
        )

        if self._check_is_wecom_message(values):
            # 如果是wecom消息，则添加相关企微消息的字段到values
            values.update(
                {
                    "is_wecom_message": True,
                    "msgtype": "markdown",
                    "body_markdown": _(
                        "### %s sent you a message,You can also view it in your inbox in the system."
                        + "\n\n"
                        + "> **Message content:**\n\n> %s"
                    )
                    % (
                        self.env.user.partner_id.browse(values["author_id"]).name,
                        values["body"],
                    ),
                    "enable_duplicate_check": True,
                    "duplicate_check_interval": 1800,
                }
            )
        else:
            values.update(
                {"is_wecom_message": False,}
            )

        attachments = attachments or []
        attachment_ids = attachment_ids or []
        attachement_values = self._message_post_process_attachments(
            attachments, attachment_ids, values
        )
        values.update(attachement_values)  # attachement_ids, [body]

        new_message = self._message_create(values)

        # Set main attachment field if necessary 如有必要，设置主附件字段
        self._message_set_main_attachment_id(values["attachment_ids"])

        if (
            values["author_id"]
            and values["message_type"] != "notification"
            and not self._context.get("mail_create_nosubscribe")
        ):
            if (
                self.env["res.partner"].browse(values["author_id"]).active
            ):  # 我们不想添加odoobot/inactive作为关注者
                self._message_subscribe([values["author_id"]])

        self._message_post_after_hook(new_message, values)
        self._notify_thread(new_message, values, **notif_kwargs)
        return new_message

    # ------------------------------------------------------
    # MESSAGE POST TOOLS
    # 消息发布工具
    # ------------------------------------------------------

    # ------------------------------------------------------
    # 通知API
    # NOTIFICATION API
    # ------------------------------------------------------

    def _notify_record_by_inbox(
        self, message, recipients_data, msg_vals=False, **kwargs
    ):
        """通知方式：收件箱。做两件主要的事情

          * 为用户创建收件箱通知;
          * 创建通道/消息链接（channel_ids mail.message 字段）;
          * 发送总线通知;

        TDE/XDO TODO: 直接标记 rdata，例如 r['notif'] = 'ocn_client' 和 r['needaction']=False 并正确覆盖notify_recipients
        """
        channel_ids = [r["id"] for r in recipients_data["channels"]]
        if channel_ids:
            message.write({"channel_ids": [(6, 0, channel_ids)]})

        inbox_pids = [
            r["id"] for r in recipients_data["partners"] if r["notif"] == "inbox"
        ]
        if inbox_pids:
            notif_create_values = [
                {
                    "mail_message_id": message.id,
                    "res_partner_id": pid,
                    "notification_type": "inbox",
                    "notification_status": "sent",
                }
                for pid in inbox_pids
            ]
            self.env["mail.notification"].sudo().create(notif_create_values)

        bus_notifications = []
        if inbox_pids or channel_ids:
            message_format_values = False
            if inbox_pids:
                message_format_values = message.message_format()[0]
                for partner_id in inbox_pids:
                    bus_notifications.append(
                        [
                            (self._cr.dbname, "ir.needaction", partner_id),
                            dict(message_format_values),
                        ]
                    )
            if channel_ids:
                channels = self.env["mail.channel"].sudo().browse(channel_ids)
                bus_notifications += channels._channel_message_notifications(
                    message, message_format_values
                )

        if msg_vals["is_wecom_message"]:
            self._notify_record_by_wecom(
                message, recipients_data, msg_vals=msg_vals, **kwargs
            )

        if bus_notifications:
            self.env["bus.bus"].sudo().sendmany(bus_notifications)

    def _notify_record_by_wecom(
        self, message, recipients_data, msg_vals=False, **kwargs
    ):
        """
        :param  message: mail.message 记录
        :param list recipients_data: 收件人
        :param dic msg_vals: 消息字典值
        """
        Model = self.env[msg_vals["model"]]
        model_name = self.env["ir.model"]._get(msg_vals["model"]).display_name

        partners = []
        if "partners" in recipients_data:
            partners = [r["id"] for r in recipients_data["partners"]]
        wecom_userids = [
            p.wecom_userid
            for p in self.env["res.partner"].browse(partners)
            if p.wecom_userid
        ]

        sender = self.env.user.partner_id.browse(msg_vals["author_id"]).name

        if msg_vals.get("subject") or message.subject:
            pass
        elif msg_vals.get("subject") and message.subject is False:
            pass
        elif msg_vals.get("subject") is False and message.subject:
            msg_vals["subject"] = message.subject
        else:
            msg_vals["subject"] = _(
                "[%s] Sends a message with the record name [%s] in the application [%s]."
            ) % (sender, Model.browse(msg_vals["res_id"]).name, model_name)

        message.write({"subject": msg_vals["subject"]})

        # company = Model.company_id
        # if not company:
        #     company = self.env.company
        # try:
        #     wecomapi = self.env["wecom.service_api"].InitServiceApi(
        #         company.corpid, company.message_app_id.secret
        #     )
        #     msg = self.env["wecom.message.api"].build_message(
        #         msgtype="markdown",
        #         touser="|".join(wecom_userids),
        #         toparty="",
        #         totag="",
        #         subject=msg_vals["subject"],
        #         media_id=None,
        #         description=None,
        #         author_id=msg_vals["author_id"],
        #         body_markdown=_(
        #             "### %s sent you a message,You can also view it in your inbox in the system."
        #             + "\n\n"
        #             + "> **Message content:**\n\n> %s"
        #         )
        #         % (sender, msg_vals["body"],),
        #         enable_duplicate_check=True,
        #         duplicate_check_interval=1800,
        #         company=company,
        #     )
        #     del msg["company"]
        # except ApiException as exc:
        #     pass
        # else:
        #     pass

    # ------------------------------------------------------
    # 关注者API
    # FOLLOWERS API
    # ------------------------------------------------------

    # ------------------------------------------------------
    # 控制器
    # CONTROLLERS
    # ------------------------------------------------------

# -*- coding: utf-8 -*-
"""
Author: PaulLei
Website: http://www.168nz.cn
Date: 2021-11-11 15:59:11
LastEditTime: 2021-11-12 23:01:05
LastEditors: PaulLei
Description: Description
"""
from odoo import _, api, fields, models
import json
from werkzeug import urls
import html2text

# TODO 向关注者发送消息。。。 Send a message to followers...
#  模型的message_post 方法


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    # ------------------------------------------------------
    # 消息推送API
    # MESSAGE POST API
    # ------------------------------------------------------

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
        在现有线程中发布新邮件，返回新的mail.message ID。
        :param str body: 消息体，通常是将被清理的原始HTML
        :param str subject: 消息的主题
        :param str message_type: 请参阅mail_message.message_type字段。可以是除用户通知之外的任何内容，保留用于消息通知
        :param int parent_id: handle thread formation
        :param int subtype_id: subtype_id的消息，主要采用前关注者机制
        :param list(int) partner_ids: 要通知的 partner_ids
        :param list(int) channel_ids: 要通知的 channel_ids to notify
        :param list(tuple(str,str), tuple(str,str, dict) or int) attachments : 表单中的附件元组列表
            ``(name,content)`` or ``(name,content, info)``, where content is NOT base64 encoded
        :param list id attachment_ids: list of existing attachement to link to this message
            -Should only be setted by chatter
            -Attachement object attached to mail.compose.message(0) will be attached
                to the related document.
        额外的关键字参数将用作新 mail.message 记录的默认列值。
        :return int:  新创建的 mail.messageID
        """
        self.ensure_one()  # 应始终张贴在记录上，如果没有记录，请使用message_notify
        # 从通知附加值中拆分消息附加值
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

        self = self._fallback_lang()  # 立即将 lang 添加到上下文中，因为它在以后的各种流中很有用。

        # 显式访问权限检查，因为display_name计算为sudo。
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
            # 在sudo中搜索parent_message以获取性能，仅用于id。
            # 注意，对于sudo，我们将消息与内部子类型匹配。
            parent_id = parent_message.id if parent_message else False
        elif parent_id:
            old_parent_id = parent_id
            parent_message = MailMessage_sudo.search(
                [("id", "=", parent_id), ("parent_id", "!=", False)], limit=1
            )
            # 查找祖先时避免循环
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
        attachments = attachments or []
        attachment_ids = attachment_ids or []
        attachement_values = self._message_post_process_attachments(
            attachments, attachment_ids, values
        )
        values.update(attachement_values)  # attachement_ids, [body]

        new_message = self._message_create(values)

        # 如有必要，设置主附件字段
        self._message_set_main_attachment_id(values["attachment_ids"])

        if (
            values["author_id"]
            and values["message_type"] != "notification"
            and not self._context.get("mail_create_nosubscribe")
        ):
            if (
                self.env["res.partner"].browse(values["author_id"]).active
            ):  # 我们不想添加odoobot/inactive 作为follower
                self._message_subscribe([values["author_id"]])

        self._message_post_after_hook(new_message, values)
        self._notify_thread(new_message, values, **notif_kwargs)
        return new_message

    # ------------------------------------------------------
    # 通知API
    # NOTIFICATION API
    # ------------------------------------------------------
    def _notify_thread(self, message, msg_vals=False, notify_by_email=True, **kwargs):
        """
        主要通知方法。这种方法基本上做两件事

         * 调用"_notify_compute_recipients"，根据给定的消息记录或消息创建值计算收件人通知（如果我们已经计算了数据，则优化性能）;
         * 通过调用实现的各种通知方法来执行通知过程;

        此方法 cnn 将被覆盖以拦截和推迟通知机制，如 mail.channel 审核。

        :param message: 要通知的 mail.message 记录；
        :param msg_vals: 用于创建消息的值的字典。如果给定它，则使用而不是访问"self"来减少查询计数，在一些实际上不需要通知的简单情况下;

        Kwargs 允许传递提供给子通知方法的各种参数。有关其他参数的更多详细信息，请参阅这些方法。
        用于电子邮件样式通知的参数
        """
        msg_vals = msg_vals if msg_vals else {}
        rdata = self._notify_compute_recipients(message, msg_vals)
        if not rdata:
            return False

        message_values = {}
        if rdata["channels"]:
            message_values["channel_ids"] = [
                (6, 0, [r["id"] for r in rdata["channels"]])
            ]
        if "wecom_userid" in self._fields:
            self._notify_record_by_wecom(message, rdata, msg_vals=msg_vals, **kwargs)
        else:
            self._notify_record_by_inbox(message, rdata, msg_vals=msg_vals, **kwargs)
            if notify_by_email:
                self._notify_record_by_email(
                    message, rdata, msg_vals=msg_vals, **kwargs
                )

        return rdata

    def _notify_record_by_wecom(
        self, message, recipients_data, msg_vals=False, **kwargs
    ):
        """
        通知方式：收件箱。做两件主要的事情

          * 为用户创建收件箱通知;
          * 创建通道/消息链接（mail.message 的 channel_ids 字段）;
          * 发送总线通知;

        TDE/XDO TODO: 直接标记 rdata， 例如 r['notif'] = 'ocn_client' 和 r['needaction']=False
        并正确覆盖 notify_recipients
        """

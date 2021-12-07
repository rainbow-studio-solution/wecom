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
import re

# TODO 向关注者发送消息。。。 Send a message to followers...
#  模型的message_post 方法


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    # ------------------------------------------------------
    # 消息推送API
    # MESSAGE POST API
    # ------------------------------------------------------

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
            msg_vals.update(
                {
                    "wecom_userid": self.env[message.model]
                    .browse(message.res_id)
                    .wecom_userid,
                }
            )
            self._notify_record_by_wecom(message, rdata, msg_vals=msg_vals, **kwargs)

        self._notify_record_by_inbox(message, rdata, msg_vals=msg_vals, **kwargs)
        if notify_by_email:
            self._notify_record_by_email(message, rdata, msg_vals=msg_vals, **kwargs)

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

        res_id = self.env[message.model].browse(message.res_id)
        company = res_id.company_id

        channel_ids = [r["id"] for r in recipients_data["channels"]]
        inbox_pids = [
            r["id"] for r in recipients_data["partners"] if r["notif"] == "inbox"
        ]

        # wecom_userids = [
        #     p.wecom_userid
        #     for p in self.env["res.partner"].browse(inbox_pids)
        #     if p.wecom_userid
        # ]

        wecom_message_values = {
            "model": msg_vals["model"],
            "res_id": msg_vals["res_id"],
            "record_name": msg_vals["record_name"],
            # "parent_id": msg_vals.parent_id,
            "subtype_id": msg_vals["subtype_id"],
            "message_type": msg_vals["message_type"],
            "author_id": msg_vals["author_id"],
            # "partner_ids": msg_vals["partner_ids"],
            # 以下为企业微信字段
            "msgtype": "markdown",
            "body_markdown": _(
                "### %s sent you a message,You can also view it in your inbox in the system."
                + "\n\n"
                + "> **Message content:**\n\n> %s"
            )
            % (
                self.env.user.partner_id.browse(msg_vals["author_id"]).name,
                msg_vals["body"],
            ),
            "message_to_user": msg_vals["wecom_userid"],
            "enable_duplicate_check": True,
            "duplicate_check_interval": 1800,
        }

        wecom_message_id = self.env["wecom.message.message"].create(
            wecom_message_values
        )
        wecom_message_id.send(
            company=company,
        )
        # if inbox_pids:
        #     notif_create_values = [
        #         {
        #             "message_message_id": wecom_message_id.id,
        #             "res_partner_id": pid,
        #             "notification_type": "inbox",
        #             "notification_status": "sent",
        #         }
        #         for pid in inbox_pids
        #     ]
        #     self.env["wecom.message.notification"].sudo().create(notif_create_values)

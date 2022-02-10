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


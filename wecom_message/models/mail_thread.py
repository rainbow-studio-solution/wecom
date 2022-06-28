# -*- coding: utf-8 -*-


import re
from email import message
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
        ir_config = self.env["ir.config_parameter"].sudo()
        message_sending_method = ir_config.get_param("wecom.message_sending_method")

        bus_notifications = []
        inbox_pids = [r["id"] for r in recipients_data if r["notif"] == "inbox"]
        if inbox_pids:
            notif_create_values = [
                {
                    "mail_message_id": message.id,
                    "res_partner_id": pid,
                    "notification_type": "inbox",
                    "notification_status": "sent",
                    "is_wecom_message": True
                    if self.env["res.partner"].browse(pid).wecom_userid
                    else False,
                }
                for pid in inbox_pids
            ]

            mail_notification = (
                self.env["mail.notification"].sudo().create(notif_create_values)
            )

            message_format_values = message.message_format()[0]
            for partner_id in inbox_pids:
                bus_notifications.append(
                    (
                        self.env["res.partner"].browse(partner_id),
                        "mail.message/inbox",
                        dict(message_format_values),
                    )
                )
            if mail_notification.is_wecom_message:
                self._notify_record_by_wecom(
                    message, recipients_data, msg_vals=msg_vals, **kwargs
                )
        if message_sending_method != "1":
            self.env["bus.bus"].sudo()._sendmany(bus_notifications)

    def _notify_record_by_wecom(
        self, message, recipients_data, msg_vals=False, **kwargs
    ):
        """
        通过企业微信发送 通知消息
        :param  message: mail.message 记录
        :param list recipients_data: 收件人
        :param dic msg_vals: 消息字典值
        """
        subject = ""
        if msg_vals:
            Model = self.env[msg_vals["model"]]
            model_name = self.env["ir.model"]._get(msg_vals["model"]).display_name
            sender = self.env.user.partner_id.browse(msg_vals["author_id"]).name
            document_name = Model.browse(msg_vals["res_id"]).name
            msg = self.env["mail.render.mixin"]._replace_local_links(msg_vals["body"])
            company = Model.browse(msg_vals["res_id"]).company_id
            author_id = msg_vals["author_id"]
            if msg_vals.get("subject"):
                subject = msg_vals.get("subject")
        else:
            Model = self.env[message["model"]]
            model_name = self.env["ir.model"]._get(message["model"]).display_name
            sender = message["author_id"].display_name
            document_name = Model.browse(message["res_id"]).name
            msg = self.env["mail.render.mixin"]._replace_local_links(message["body"])

            company = Model.browse(message["res_id"]).company_id
            author_id = message["author_id"].id
            if message["subject"]:
                subject = message["subject"]
        msg = re.compile(r"<[^>]+>", re.S).sub("", msg)
        wecom_userids = [
            self.env["res.partner"].browse(r["id"]).wecom_userid
            for r in recipients_data
            if self.env["res.partner"].browse(r["id"]).wecom_userid
        ]

        body_markdown = (
            _(
                """
**[%s] send a message with the record name [%s] in the application [%s].**
>
> <font color="warning">%s</font>
>
> <font color="info">Message content:</font>
>              
> %s
>
"""
            )
            % (sender, document_name, model_name, subject, msg,)
        )

        if len(message.attachment_ids) > 0:
            body_markdown = (
                _(
                    """
 **[%s] send a message with the record name [%s] in the application [%s].**
>
> <font color="warning">%s</font>
>
> <font color="info">Message content:</font>
>              
> %s


> The message contains %s attachments   
>
> Please log in to the system to view.     
            """
                )
                % (
                    sender,
                    document_name,
                    model_name,
                    subject,
                    msg,
                    len(message.attachment_ids),
                )
            )

        message.write(
            {
                "subject": subject,
                "message_to_user": "|".join(wecom_userids),
                "message_to_party": None,
                "message_to_tag": None,
                "msgtype": "markdown",
                "body_markdown": body_markdown,
                "is_wecom_message": True,
            }
        )

        if not company:
            company = self.env.company
        try:
            wecomapi = self.env["wecom.service_api"].InitServiceApi(
                company.corpid, company.message_app_id.secret
            )
            msg = self.env["wecom.message.api"].build_message(
                msgtype="markdown",
                touser="|".join(wecom_userids),
                toparty="",
                totag="",
                subject=subject,
                media_id=None,
                description=None,
                author_id=author_id,
                body_markdown=body_markdown,
                safe=True,
                enable_id_trans=True,
                enable_duplicate_check=True,
                duplicate_check_interval=1800,
                company=company,
            )

            del msg["company"]
            res = wecomapi.httpCall(
                self.env["wecom.service_api_list"].get_server_api_call("MESSAGE_SEND"),
                msg,
            )
        except ApiException as exc:
            error = self.env["wecom.service_api_error"].get_error_by_code(exc.errCode)
            message.write(
                {
                    "state": "exception",
                    "failure_reason": "%s %s" % (str(error["code"]), error["name"]),
                }
            )
        else:
            message.write(
                {"state": "sent", "wecom_message_id": res["msgid"],}
            )

    # ------------------------------------------------------
    # 关注者API
    # FOLLOWERS API
    # ------------------------------------------------------

    # ------------------------------------------------------
    # 控制器
    # CONTROLLERS
    # ------------------------------------------------------

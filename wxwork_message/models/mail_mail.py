# -*- coding: utf-8 -*-

import datetime
import logging
import threading
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.addons.wxwork_api.api.corp_api import CorpApi, CORP_API_TYPE

_logger = logging.getLogger(__name__)


class MailMail(models.Model):
    _inherit = "mail.mail"

    message_to_all = fields.Boolean("To all members",)
    message_to_user = fields.Char(string="To User",)
    message_to_party = fields.Char(string="To Departments",)
    message_to_tag = fields.Char(string="To Tags",)
    body_text = fields.Text("Text Contents",)

    safe = fields.Selection(
        [
            ("0", "Shareable"),
            ("1", "Cannot share and content shows watermark"),
            ("2", "Only share within the company "),
        ],
        string="Secret message",
        required=True,
        default="1",
        readonly=True,
        help="表示是否是保密消息，0表示可对外分享，1表示不能分享且内容显示水印，2表示仅限在企业内分享，默认为0；注意仅mpnews类型的消息支持safe值为2，其他消息类型不支持",
    )

    enable_id_trans = fields.Boolean(
        string="Turn on id translation", help="表示是否开启id转译，0表示否，1表示是，默认0", default=False
    )
    enable_duplicate_check = fields.Boolean(
        string="Turn on duplicate message checking",
        help="表示是否开启重复消息检查，0表示否，1表示是，默认0",
        default=False,
    )
    duplicate_check_interval = fields.Integer(
        string="Time interval for repeated message checking",
        help="表示是否重复消息检查的时间间隔，默认1800s，最大不超过4小时",
        default="1800",
    )

    @api.model
    def process_email_queue(self, ids=None):
        """
        立即发送排队的消息，在每条消息发送后提交-这不是事务性的，不应在另一个事务中调用！ 

        :param list ids: 要发送的电子邮件ID的可选列表。 如果通过，则不执行搜索，而是使用这些ID。 
        :param dict context: 如果上下文中存在“过滤器”键，则此值将用作附加过滤器，以进一步限制要发送的传出消息（默认情况下，所有“传出”消息都已发送）。 
        """
        filters = [
            "&",
            ("state", "=", "outgoing"),
            "|",
            ("scheduled_date", "<", datetime.datetime.now()),
            ("scheduled_date", "=", False),
        ]
        if "filters" in self._context:
            filters.extend(self._context["filters"])
        # TODO: make limit configurable
        filtered_ids = self.search(filters, limit=10000).ids
        if not ids:
            ids = filtered_ids
        else:
            ids = list(set(filtered_ids) & set(ids))
        ids.sort()

        res = None
        try:
            # 自动提交（测试模式除外）
            auto_commit = not getattr(threading.currentThread(), "testing", False)
            if self.notification_type == "wxwork":
                res = self.browse(ids).send_wxwork_message(auto_commit=auto_commit)
            else:
                res = self.browse(ids).send(auto_commit=auto_commit)
        except Exception:
            _logger.exception(_("Failed processing mail queue"))
        return res

    def send_wxwork_message(self, auto_commit=False, raise_exception=False):
        """
        立即发送选定的电子邮件，而忽略它们的当前状态（除非已被重新发送，否则不应传递已发送的电子邮件）。
成功发送的电子邮件被标记为“已发送”，而失败发送的电子邮件被标记为“例外”，并且相应的错误邮件将输出到服务器日志中。
        :param bool auto_commit：发送每封邮件后是否强制提交邮件状态（仅用于调度程序处理）；
                 在正常发送绝对不能为True（默认值：False） 
        :param bool raise_exception：如果电子邮件发送过程失败，是否引发异常 
        :return: True
        """

        sys_params = self.env["ir.config_parameter"].sudo()
        corpid = sys_params.get_param("wxwork.corpid")
        secret = sys_params.get_param("wxwork.message_secret")
        message_agentid = sys_params.get_param("wxwork.message_agentid")

        if "xxxxxxxxxxxxxxxxxx" in corpid:
            raise UserError(_("Please fill in the company ID"))
        elif "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" in secret:
            raise UserError(
                _("Please fill in the application secret of the message push")
            )
        elif "0000000" in message_agentid:
            raise UserError(_("Please fill in the application ID of the message push"))
        else:
            wxapi = CorpApi(corpid, secret)
            for batch_ids in self._split_by_server():
                self.browse(batch_ids)._send_wxwork_message(
                    auto_commit=auto_commit,
                    raise_exception=raise_exception,
                    wxapi=wxapi,
                )
                _logger.info(
                    _("Sent batch %s messages"), len(batch_ids),
                )

    def _send_wxwork_message(
        self, auto_commit=False, raise_exception=False, wxapi=None
    ):
        for mail_id in self.ids:
            success_pids = []
            failure_type = None
            processing_pid = None
            mail = None
            try:
                mail = self.browse(mail_id)
                if mail.state != "outgoing":
                    if mail.state != "exception" and mail.auto_delete:
                        mail.sudo().unlink()
                    continue

                # 如果用户发送带有access_token的链接，则删除附件
                # body_html = mail.body_html or ""
                # body_text = mail.body_text or ""

                email_list = []
                if mail.email_to:
                    email_list.append(mail._send_prepare_values())
                for partner in mail.recipient_ids:
                    values = mail._send_prepare_values(partner=partner)
                    values["partner_id"] = partner
                    email_list.append(values)
                # 在邮件对象上写入可能会失败（例如，锁定用户），这会在实际发送电子邮件后*触发回滚。
                # 为避免发送两次相同的电子邮件，请尽早引发故障
                mail.write(
                    {
                        "state": "exception",
                        "failure_reason": _(
                            "Error without exception. Probably due do sending an email without computed recipients."
                        ),
                    }
                )
                # 在临时异常状态下更新通知，以避免在发送与当前邮件记录相关的所有电子邮件时邮件退回的情况下并发更新。
                notifs = self.env["mail.notification"].search(
                    [
                        ("notification_type", "=", "wxwork"),
                        ("mail_id", "in", mail.ids),
                        ("notification_status", "not in", ("sent", "canceled")),
                    ]
                )
                if notifs:
                    notif_msg = _(
                        "Error without exception. Probably due do concurrent access update of notification records. Please see with an administrator."
                    )
                    notifs.sudo().write(
                        {
                            "notification_status": "exception",
                            "failure_type": "UNKNOWN",
                            "failure_reason": notif_msg,
                        }
                    )
                    # `test_mail_bounce_during_send`，强制立即更新以获取锁。
                    # see rev. 56596e5240ef920df14d99087451ce6f06ac6d36
                    notifs.flush(
                        fnames=[
                            "notification_status",
                            "failure_type",
                            "failure_reason",
                        ],
                        records=notifs,
                    )

                # 构建一个email.message.Message对象并发送它而不排队
                res = None
            except MemoryError:
                # 防止捕获短暂的MemoryErrors，冒泡通知用户或中止cron作业，而不是将邮件标记为失败
                _logger.exception(
                    "MemoryError while processing mail with ID %r and Msg-Id %r. Consider raising the --limit-memory-hard startup option",
                    mail.id,
                    mail.message_id,
                )
                # mail status will stay on ongoing since transaction will be rollback
                raise

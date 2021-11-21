# -*- coding: utf-8 -*-

import datetime
import logging
import threading
from odoo import _, api, fields, models
from odoo import tools
from odoo.addons.base.models.ir_mail_server import MailDeliveryException
from odoo.exceptions import UserError, Warning

from odoo.addons.wecom_api.api.error_code import Errcode

_logger = logging.getLogger(__name__)


class MailMail(models.Model):
    _inherit = "mail.mail"

    is_wecom_message = fields.Boolean("WeCom Message")
    msgtype = fields.Char(
        string="Message type",
    )
    media_id = fields.Char(
        string="Media file id",
    )
    message_to_all = fields.Boolean(
        "To all members",
    )
    message_to_user = fields.Char(
        string="To User",
    )
    message_to_party = fields.Char(
        string="To Departments",
    )
    message_to_tag = fields.Char(
        string="To Tags",
    )
    body_not_html = fields.Text(
        "Text Contents",
    )
    body_html = fields.Text(
        "Html Contents",
    )

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

    def _postprocess_sent_wecom_message(
        self, success_pids, failure_reason=False, failure_type=None
    ):
        """
        成功发送``mail``后，请执行所有必要的后处理，包括如果已设置邮件的auto_delete标志，则将其及其附件完全删除。
        被子类覆盖，以实现额外的后处理行为。

        :return: True
        """
        notif_mails_ids = [mail.id for mail in self if mail.notification]
        if notif_mails_ids:
            notifications = self.env["mail.notification"].search(
                [
                    ("notification_type", "=", "email"),
                    ("is_wecom_message", "=", True),
                    ("mail_id", "in", notif_mails_ids),
                    ("notification_status", "not in", ("sent", "canceled")),
                ]
            )
            if notifications:
                # 查找所有链接到失败的通知
                failed = self.env["mail.notification"]
                if failure_type:
                    failed = notifications.filtered(
                        lambda notif: notif.res_partner_id not in success_pids
                    )
                (notifications - failed).sudo().write(
                    {
                        "notification_status": "sent",
                        "is_wecom_message": True,
                        "failure_type": "",
                        "failure_reason": "",
                    }
                )
                if failed:
                    failed.sudo().write(
                        {
                            "notification_status": "exception",
                            "is_wecom_message": True,
                            "failure_type": failure_type,
                            "failure_reason": failure_reason,
                        }
                    )
                    messages = notifications.mapped("mail_message_id").filtered(
                        lambda m: m.is_thread_message()
                    )
                    # TDE TODO: 通知基于消息而不是基于通知的通知，以减少通知数量可能会很棒
                    messages._notify_message_notification_update()  # 通知用户我们失败了
            if not failure_type or failure_type == "RECIPIENT":  # 如果还有另一个错误，我们要保留邮件。
                mail_to_delete_ids = [mail.id for mail in self if mail.auto_delete]
                self.browse(mail_to_delete_ids).sudo().unlink()

        return True

    # ------------------------------------------------------
    # 消息格式、工具和发送机制
    # mail_mail formatting, tools and send mechanism
    # ------------------------------------------------------
    def send(
        self,
        auto_commit=False,
        raise_exception=False,
        is_wecom_message=None,
        company=None,
    ):
        """
        立即发送选定的电子邮件，而忽略它们的当前状态（除非已被重新发送，否则不应该传递已经发送的电子邮件）。
        成功发送的电子邮件被标记为“已发送”，未发送成功的电子邮件被标记为“例外”，并且相应的错误邮件将输出到服务器日志中。

        :param bool auto_commit: 在发送每封邮件后是否强制提交邮件状态（仅用于调度程序处理）；
            在正常传递中，永远不应该为True（默认值：False）
        :param bool raise_exception: 如果电子邮件发送过程失败，将引发异常
        :param bool is_wecom_message: 标识是企业微信消息
        :param company: 公司
        :return: True
        """
        # print(self)
        if not company:
            company = self.env.company
        if is_wecom_message is None:
            if self.mapped("message_to_user"):
                is_wecom_message = True
            else:
                is_wecom_message = False

        for server_id, batch_ids in self._split_by_server():
            smtp_session = None
            try:
                if is_wecom_message:
                    pass
                else:
                    smtp_session = self.env["ir.mail_server"].connect(
                        mail_server_id=server_id
                    )
            except Exception as exc:
                if is_wecom_message:
                    pass
                else:
                    if raise_exception:
                        # 为了与mail_mail.send（）引发的异常保持一致并向后兼容，将其封装到Odoo MailDeliveryException中
                        raise MailDeliveryException(
                            _("Unable to connect to SMTP Server"), exc
                        )
                    else:
                        batch = self.browse(batch_ids)
                        batch.write({"state": "exception", "failure_reason": exc})
                        batch._postprocess_sent_message(
                            success_pids=[], failure_type="SMTP"
                        )
            else:
                # 当没有异常发生时,执行else
                if is_wecom_message:
                    pass
                else:
                    self.browse(batch_ids)._send(
                        auto_commit=auto_commit,
                        raise_exception=raise_exception,
                        smtp_session=smtp_session,
                    )
                    _logger.info(
                        _("Sent batch %s emails via mail server ID #%s"),
                        len(batch_ids),
                        server_id,
                    )
            finally:
                if is_wecom_message:
                    self.browse(batch_ids)._send_wecom_message(
                        auto_commit=auto_commit,
                        raise_exception=raise_exception,
                        company=company,
                    )

                    # if raise_exception:
                    #     self.browse(batch_ids)._send_wecom_message(
                    #         auto_commit=auto_commit, raise_exception=raise_exception,
                    #     )

                    # else:
                    #     batch = self.browse(batch_ids)
                    #     batch.write({"state": "exception", "failure_reason": ""})
                    #     batch._postprocess_sent_wecom_message(success_pids=[],)
                    _logger.info(
                        _("Sent batch %s message via WeCom "),
                        len(batch_ids),
                    )
                else:
                    if smtp_session:
                        smtp_session.quit()

    def _send_message_prepare_body(self):
        """
        返回特定的ir_email正文。 继承此方法的主要目的是根据某些模块添加自定义内容。
        """
        self.ensure_one()
        return self.body_html or ""

    def _send_message_prepare_values(self, partner=None):
        """
        根据合作伙伴返回特定电子邮件值的字典，或者返回由mail.message_to_user mail.message_to_party  mail.message_to_tag 给出的整个收件人通用的字典。
        :param Model partner: 具体的收件人合作伙伴
        """
        self.ensure_one()
        body = self._send_message_prepare_body()
        body_alternative = tools.html2plaintext(body)
        if partner:
            message_to_user = [
                tools.formataddr((partner.name or "False", partner.wecom_id or "False"))
            ]
        else:
            message_to_user = tools.email_split_and_format(self.email_to)
        res = {
            "body": body,
            "body_alternative": body_alternative,
            "message_to_user": message_to_user,
        }
        return res

    def _send_wecom_prepare_values(self, partner=None):
        """
        根据合作伙伴返回有关特定电子邮件值的字典，或者对整个邮件都是通用的。对于特定电子邮件值取决于对伙伴的字典，或者对mail.email_to给出的整个收件人来说都是通用的。
        :param Model partner: 具体的收件人合作伙伴
        """
        self.ensure_one()
        body_html = self._send_prepare_body()
        # body_alternative = tools.html2plaintext(body_html)
        if partner:
            email_to = [
                tools.formataddr((partner.name or "False", partner.email or "False"))
            ]
            message_to_user = [
                tools.formataddr((partner.name or "False", partner.wecom_id or "False"))
            ]
        else:
            email_to = tools.email_split_and_format(self.email_to)
            message_to_user = self.message_to_user
        res = {
            # "body_not_html": body_not_html,
            # "body_html": body_html,
            "email_to": email_to,
            "message_to_user": message_to_user,
        }

        return res

    def send_wecom_message(self, auto_commit=False, raise_exception=False):
        """
                立即发送选定的电子邮件，而忽略它们的当前状态（除非已被重新发送，否则不应传递已发送的电子邮件）。
        成功发送的电子邮件被标记为“已发送”，而失败发送的电子邮件被标记为“例外”，并且相应的错误邮件将输出到服务器日志中。
                :param bool auto_commit：发送每封邮件后是否强制提交邮件状态（仅用于调度程序处理）；
                         在正常发送绝对不能为True（默认值：False）
                :param bool raise_exception：如果电子邮件发送过程失败，是否引发异常
                :return: True
        """

        # TODO 待处理各类型的接收者

        sys_params = self.env["ir.config_parameter"].sudo()

        employee = (
            self.env["hr.employee"]
            .sudo()
            .search(
                [
                    ("wecom_id", "=", self.message_to_user),
                    "|",
                    ("active", "=", True),
                    ("active", "=", False),
                ],
            )
        )
        company = employee.company_id
        corpid = company.corpid
        secret = company.message_secret
        message_agentid = company.message_agentid

        if "xxxxxxxxxxxxxxxxxx" in corpid or corpid is None or corpid is False:
            raise UserError(_("Please fill in the company ID"))
        elif (
            "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" in secret
            or secret is None
            or secret is False
        ):
            raise UserError(
                _("Please fill in the application secret of the message push")
            )
        elif (
            "0000000" in message_agentid
            or message_agentid is None
            or message_agentid is False
        ):
            raise UserError(_("Please fill in the application ID of the message push"))
        else:
            for batch_ids in self._split_by_server():
                # TODO 待处理多公司-企业微信互联功能

                self.browse(batch_ids)._send_wecom_message(
                    auto_commit=auto_commit,
                    raise_exception=raise_exception,
                    company=company,
                )
                _logger.info(
                    _("Sent batch %s messages"),
                    len(batch_ids),
                )

    def _send_wecom_message(
        self,
        auto_commit=False,
        raise_exception=False,
        company=None,
    ):
        """
        :param bool auto_commit: 发送每封邮件后是否强制提交邮件状态（仅用于调度程序处理）；
                 在正常发送绝对不能为True（默认值：False）
        :param bool raise_exception: 如果电子邮件发送过程失败，是否引发异常
        :return: True
        """

        if not company:
            company = self.env.company

        IrWxWorkMessageApi = self.env["wecom.message.api"]
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
                # 为通知的合作伙伴自定义发送电子邮件的特定行为
                email_list = []
                if mail.message_to_user or mail.message_to_party or mail.message_to_tag:
                    email_list.append(mail._send_wecom_prepare_values())
                for partner in mail.recipient_ids:
                    values = mail._send_wecom_prepare_values(partner=partner)
                    values["partner_id"] = partner
                    email_list.append(values)

                # 在邮件对象上写入可能会失败（例如锁定用户），这将在*实际发送电子邮件后触发回滚。
                # 为了避免两次发送同一封电子邮件，请尽早引发失败

                mail.write(
                    {
                        "is_wecom_message": True,
                        "state": "sent",
                        # "state": "exception",
                        # "failure_reason": _(
                        #     "Error without exception. Probably due do sending an message without computed recipients."
                        # ),
                    }
                )

                # 在临时异常状态下更新通知，以避免在发送与当前邮件记录相关的所有电子邮件时发生电子邮件反弹的情况下进行并发更新。

                notifs = self.env["mail.notification"].search(
                    [
                        ("notification_type", "=", "email"),
                        ("is_wecom_message", "=", True),
                        ("mail_id", "in", mail.ids),
                        ("notification_status", "not in", ("sent", "canceled")),
                    ]
                )
                if notifs:
                    # TODO: 待处理
                    notif_msg = _(
                        "Error without exception. Probably due do concurrent access update of notification records. Please see with an administrator."
                    )
                    notifs.sudo().write(
                        {
                            # "notification_status": "exception",
                            "notification_status": "send",
                            # "failure_type": "UNKNOWN",
                            # "failure_reason": notif_msg,
                        }
                    )
                    # `test_mail_bounce_during_send`，强制立即更新以获取锁定。
                    # 见修订版。56596e5240ef920df14d99087451ce6f06ac6d36
                    notifs.flush(
                        fnames=[
                            "notification_status",
                            "failure_type",
                            "failure_reason",
                        ],
                        records=notifs,
                    )
                # TODO 带处理获取素材

                # 建立电子邮件.message.message对象并在不排队的情况下发送它
                res = None
                for email in email_list:
                    msg = IrWxWorkMessageApi.build_message(
                        msgtype=mail.msgtype,
                        toall=mail.message_to_all,
                        touser=mail.message_to_user,
                        toparty=mail.message_to_party,
                        totag=mail.message_to_tag,
                        subject=mail.subject,
                        media_id=mail.media_id,
                        description=mail.description,
                        author_id=mail.author_id,
                        body_html=mail.body_html,
                        body_json=mail.body_not_html,
                        safe=mail.safe,
                        enable_id_trans=mail.enable_id_trans,
                        enable_duplicate_check=mail.enable_duplicate_check,
                        duplicate_check_interval=mail.duplicate_check_interval,
                        company=company,
                    )

                    processing_pid = email.pop("partner_id", None)
                    try:
                        res = IrWxWorkMessageApi.send_by_api(msg)
                        if processing_pid:
                            success_pids.append(processing_pid)
                        processing_pid = None
                    except AssertionError as error:
                        pass

                if res:  # 消息已至少发送一次，未发生重大异常
                    if "errcode" in str(res):
                        if res.get("errcode") == 0:
                            failure_reason = ""
                            # 处理无效的接收人
                            if "invaliduser" in res:
                                if res.get("invaliduser") != "":
                                    failure_reason += _(
                                        "Unable to send to invalid user: %s\n"
                                    ) % res.get("invaliduser")
                            if "invalidparty" in res:
                                if res.get("invalidparty") != "":
                                    failure_reason += _(
                                        "Unable to send to invalid department: %s\n"
                                    ) % res.get("invalidparty")
                            if "invalidtag" in res:
                                if res.get("invalidtag") != "":
                                    failure_reason += _(
                                        "Unable to send to invalid tag: %s"
                                    ) % res.get("invalidtag")
                            mail.write(
                                {
                                    "is_wecom_message": True,
                                    "state": "sent",
                                    "message_id": res,
                                    "failure_reason": False,
                                }
                            )

                            _logger.info(
                                _(
                                    "Message with ID %r successfully sent",
                                    mail.id,
                                )
                            )
                        else:
                            failure_reason = _(
                                "Error code: %s,\nError description: %s,\nError Details: %s"
                            ) % (
                                str(res.get("errcode")),
                                Errcode.getErrcode(res.get("errcode")),
                                res.get("errmsg"),
                            )
                            _logger.exception(
                                _("failed sending message (id: %s) due to %s")
                                % (
                                    mail.id,
                                    failure_reason,
                                )
                            )
                            mail.write(
                                {
                                    "message_type": "email",
                                    "is_wecom_message": True,
                                    "state": "exception",
                                    "failure_reason": failure_reason,
                                }
                            )
                    else:
                        raise Warning(res)
                    # raise
                else:
                    failure_reason = _("Unknown reason")
                    _logger.exception(
                        _("failed sending message (id: %s) due to %s")
                        % (
                            mail.id,
                            failure_reason,
                        )
                    )
                    mail.write(
                        {
                            "message_type": "email",
                            "is_wecom_message": True,
                            "state": "exception",
                            "failure_reason": failure_reason,
                        }
                    )
                # mail._postprocess_sent_wecom_message(
                #     success_pids=success_pids, failure_type=failure_type
                # )
            except MemoryError:
                # 防止捕获短暂的MemoryErrors，冒泡通知用户或中止cron作业，而不是将邮件标记为失败
                _logger.exception(
                    "MemoryError while processing mail with ID %r and Msg-Id %r. Consider raising the --limit-memory-hard startup option",
                    mail.id,
                    mail.message_id,
                )
                # 邮件状态将保持为正在进行状态，因为事务将被回滚
                raise

            if auto_commit is True:
                self._cr.commit()
        return True

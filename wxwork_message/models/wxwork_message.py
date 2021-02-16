# -*- coding: utf-8 -*-

import logging
import threading

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class WxWorkMessage(models.Model):
    _name = "wxwork.message"
    _description = "Outgoing Enterprise WeChat Message"
    # _rec_name = "number"
    _order = "id DESC"

    API_TO_MESSAGE_STATE = {
        "success": "sent",
        "invaliduser": "Invalid user",
        "invalidparty": "Invalid party",
        "invalidtag": "Invalid tag",
        "api_error": "Api error",
    }
    name = fields.Char(string="Name", required=True,)
    to_all = fields.Boolean("To all members", readonly=True,)
    to_user = fields.Many2many(
        "hr.employee",
        string="To Employees",
        domain="[('active', '=', True), ('is_wxwork_employee', '=', True)]",
        help="Message recipients (users)",
    )
    to_party = fields.Many2many(
        "hr.department",
        string="To Departments",
        domain="[('active', '=', True), ('is_wxwork_department', '=', True)]",
        help="Message recipients (departments)",
    )
    to_tag = fields.Many2many(
        "hr.employee.category",
        # "employee_category_rel",
        # "emp_id",
        # "category_id",
        string="To Tags",
        domain="[('is_wxwork_category', '=', True)]",
        help="Message recipients (tags)",
    )
    use_templates = fields.Boolean("Test template message",)
    templates_id = fields.Many2one("wxwork.message.template", string="Message template")
    msgtype = fields.Selection(
        [
            ("text", "Text message"),
            ("image", "Picture message"),
            ("voice", "Voice messages"),
            ("video", "Video message"),
            ("file", "File message"),
            ("textcard", "Text card message"),
            ("news", "Graphic message"),
            ("mpnews", "Graphic message（mpnews）"),
            ("markdown", "Markdown message"),
            ("miniprogram", "Mini Program Notification Message"),
            ("taskcard", "Task card message"),
        ],
        string="Message type",
        required=True,
        default="text",
    )
    body = fields.Text()
    partner_id = fields.Many2one("res.partner", "Customer")
    mail_message_id = fields.Many2one("mail.message", index=True)
    state = fields.Selection(
        [
            ("outgoing", "In Queue"),
            ("sent", "Sent"),
            ("error", "Error"),
            ("canceled", "Canceled"),
        ],
        "SMS Status",
        readonly=True,
        copy=False,
        default="outgoing",
        required=True,
    )
    error_code = fields.Selection(
        [
            ("invaliduser", "Invalid User"),
            ("invalidparty", "Invalid Department"),
            ("invalidtag", "Invalid Tag"),
        ],
        copy=False,
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

    @api.onchange("use_templates")
    def _onchange_use_templates(self):
        if self.use_templates:
            self.to_party = None
            self.to_tag = None
            if len(self.to_user) > 1:
                raise UserError(
                    _(
                        "In the test template message mode, only one user is allowed to send."
                    )
                )
            else:
                pass
        else:
            self.body = None

    @api.onchange("templates_id")
    def _onchange_templates_id(self):
        if self.templates_id:
            mail_template_info = (
                self.env["wxwork.message.template"]
                .browse(self.templates_id.id)
                .read(
                    [
                        "id",
                        "subject",
                        "body",
                        "msgtype",
                        "safe",
                        "enable_id_trans",
                        "enable_duplicate_check",
                        "duplicate_check_interval",
                    ]
                )
            )

            self.body = (
                mail_template_info[0]["subject"]
                + "\n\n"
                + mail_template_info[0]["body"]
            )
            self.msgtype = mail_template_info[0]["msgtype"]
            self.safe = mail_template_info[0]["safe"]
            self.enable_id_trans = mail_template_info[0]["enable_id_trans"]
            self.enable_duplicate_check = mail_template_info[0][
                "enable_duplicate_check"
            ]
            self.duplicate_check_interval = mail_template_info[0][
                "duplicate_check_interval"
            ]

    def send(self, delete_all=False, auto_commit=False, raise_exception=False):
        """ 
        发送企业微信消息的主要API方法。 

          :param delete_all: 删除所有企业微信消息（发送或不发送）； 否则，仅删除发送的企业微信消息； 
          :param auto_commit: 每批企业微信消息后提交； 
          :param raise_exception: raise if there is an issue contacting IAP;
        """
        for batch_ids in self._split_batch():
            self.browse(batch_ids)._send(
                delete_all=delete_all, raise_exception=raise_exception
            )
            # auto-commit if asked except in testing mode
            if auto_commit is True and not getattr(
                threading.currentThread(), "testing", False
            ):
                self._cr.commit()

    def cancel(self):
        self.state = "canceled"

    @api.model
    def _process_queue(self, ids=None):
        """ 
        立即发送排队的消息，在每条消息发送后提交。 
        这不是事务性的，不应在另一个事务中调用！

       :param list ids: 要发送的电子邮件ID的可选列表。 如果通过，则不执行搜索，而是使用这些ID。 
        """
        domain = [("state", "=", "outgoing")]

        filtered_ids = self.search(
            domain, limit=10000
        ).ids  # TDE note: arbitrary limit we might have to update
        if ids:
            ids = list(set(filtered_ids) & set(ids))
        else:
            ids = filtered_ids
        ids.sort()

        res = None
        try:
            # 自动提交（测试模式除外）
            auto_commit = not getattr(threading.currentThread(), "testing", False)
            res = self.browse(ids).send(
                delete_all=False, auto_commit=auto_commit, raise_exception=False
            )
        except Exception:
            _logger.exception(_("Failed processing Enterprise WeChat message queue"))
        return res

    def _split_batch(self):
        wxwork_message_size = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("wxwork.message.batch.size", 500)
        )
        for wxwork_message_batch in tools.split_every(wxwork_message_size, self.ids):
            yield wxwork_message_batch

    def _send(self, delete_all=False, raise_exception=False):
        """ 
        此方法在检查消息（状态和格式）后尝试发送消息。
        """

        api_data = [
            {
                "res_id": record.id,
                "recipient": {
                    "to_user": record.to_user.wxwork_id,
                    "to_party": record.to_party.wxwork_department_id,
                    "to_tag": record.to_tag.tagid,
                },
                "msgtype": record.msgtype,
                "message": record.body,
                "options": {
                    "safe": int(record.safe),
                    "enable_id_trans": int(record.enable_id_trans),
                    "enable_duplicate_check": int(record.enable_duplicate_check),
                    "duplicate_check_interval": record.duplicate_check_interval,
                },
            }
            for record in self
        ]

        try:
            api_results = self.env["wxwork.message.api"]._send_wxwork_message_batch(
                api_data
            )
        except Exception as e:
            _logger.info(
                _(
                    "Sent batch %s Enterprise WeChat Message: %s: failed with exception %s"
                ),
                len(self.ids),
                self.name,
                e,
            )
            if raise_exception:
                raise
            # self._postprocess_api_sent_message(
            #     [{"res_id": message.id, "state": "api_error"} for message in self],
            #     delete_all=delete_all,
            # )
        else:
            _logger.info(
                _("Send batch %s Enterprise WeChat Message: %s: gave %s"),
                len(self.ids),
                self.ids,
                api_results,
            )
            # self._postprocess_api_sent_message(api_results, delete_all=delete_all)

    def _postprocess_api_sent_message(
        self, api_results, failure_reason=None, delete_all=False
    ):
        if delete_all:
            todelete_message_ids = [item["res_id"] for item in api_results]
        else:
            todelete_message_ids = [
                item["res_id"] for item in api_results if item["state"] == "success"
            ]

        for state in self.API_TO_MESSAGE_STATE.keys():
            message_ids = [
                item["res_id"] for item in api_results if item["state"] == state
            ]
            if message_ids:
                if state != "success" and not delete_all:
                    self.env["wxwork.message"].sudo().browse(message_ids).write(
                        {
                            "state": "error",
                            "error_code": self.API_TO_MESSAGE_STATE[state],
                        }
                    )
                notifications = (
                    self.env["mail.notification"]
                    .sudo()
                    .search(
                        [
                            ("notification_type", "=", "wxwork"),
                            ("message_id", "in", message_ids),
                            ("notification_status", "not in", ("sent", "canceled")),
                        ]
                    )
                )
                if notifications:
                    notifications.write(
                        {
                            "notification_status": "sent"
                            if state == "success"
                            else "exception",
                            "failure_type": self.API_TO_MESSAGE_STATE[state]
                            if state != "success"
                            else False,
                            "failure_reason": failure_reason
                            if failure_reason
                            else False,
                        }
                    )
        self.mail_message_id._notify_message_notification_update()

        if todelete_message_ids:
            self.browse(todelete_message_ids).sudo().unlink()

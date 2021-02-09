# -*- coding: utf-8 -*-

import logging
import threading

from odoo import api, fields, models, tools

_logger = logging.getLogger(__name__)


class WxWorkMessage(models.Model):
    _name = "wxwork.message"
    _description = "Outgoing Enterprise WeChat Message"
    _rec_name = "number"
    _order = "id DESC"

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
        iap_data = [
            {"res_id": record.id, "number": record.number, "content": record.body,}
            for record in self
        ]

        try:
            iap_results = self.env["wxwork.message"]._send_sms_batch(iap_data)
        except Exception as e:
            _logger.info(
                _(
                    "Sent batch %s Enterprise WeChat Message: %s: failed with exception %s"
                ),
                len(self.ids),
                self.ids,
                e,
            )
            if raise_exception:
                raise
            self._postprocess_iap_sent_sms(
                [{"res_id": sms.id, "state": "server_error"} for sms in self],
                delete_all=delete_all,
            )
        else:
            _logger.info(
                "Send batch %s SMS: %s: gave %s", len(self.ids), self.ids, iap_results
            )
            self._postprocess_iap_sent_sms(iap_results, delete_all=delete_all)

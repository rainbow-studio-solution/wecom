# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError
from odoo.tools.translate import _


class WecomMessageNotification(models.Model):
    _name = "wecom.message.notification"
    _table = "wecom_message_message_res_partner_needaction_rel"
    _rec_name = "res_partner_id"
    _log_access = False
    _description = "Wecom Message Notifications"

    # origin
    message_message_id = fields.Many2one(
        "wecom.message.message",
        "Message",
        index=True,
        ondelete="cascade",
        required=True,
    )

    # recipient
    res_partner_id = fields.Many2one(
        "res.partner", "Recipient", index=True, ondelete="cascade"
    )

    # status
    notification_type = fields.Selection(
        [("inbox", "Inbox"), ("email", "Email")],
        string="Notification Type",
        default="inbox",
        index=True,
        required=True,
    )
    notification_status = fields.Selection(
        [
            ("sent", "Sent"),
            ("exception", "Send exception"),
            ("cancel", "Cancelled"),
        ],
        string="Status",
        index=True,
    )

    failure_reason = fields.Text("Failure reason", copy=False)

    # _sql_constraints = [
    #     # email notification;: partner is required
    #     (
    #         "notification_partner_required",
    #         "CHECK(notification_type NOT IN ('email', 'inbox') OR res_partner_id IS NOT NULL)",
    #         "Customer is required for inbox / email notification",
    #     ),
    # ]

    # def init(self):
    #     self._cr.execute(
    #         "SELECT indexname FROM pg_indexes WHERE indexname = %s",
    #         (
    #             "wecom_message_notification_res_partner_id_is_read_notification_status_message_message_id",
    #         ),
    #     )
    #     if not self._cr.fetchone():
    #         self._cr.execute(
    #             """
    #             CREATE INDEX wecom_message_notification_res_partner_id_is_read_notification_status_message_message_id
    #                       ON wecom_message_message_res_partner_needaction_rel (res_partner_id,  notification_status, message_message_id)
    #         """
    #         )

    # @api.model_create_multi
    # def create(self, vals_list):
    #     messages = self.env['mail.message'].browse(vals['mail_message_id'] for vals in vals_list)
    #     messages.check_access_rights('read')
    #     messages.check_access_rule('read')
    #     for vals in vals_list:
    #         if vals.get('is_read'):
    #             vals['read_date'] = fields.Datetime.now()
    #     return super(WecomMessageNotification, self).create(vals_list)

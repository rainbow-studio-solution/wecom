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
    # mail_id = fields.Many2one(
    #     "mail.mail",
    #     "Mail",
    #     index=True,
    #     help="Optional mail_mail ID. Used mainly to optimize searches.",
    # )

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
    # is_read = fields.Boolean("Is Read", index=True)
    # read_date = fields.Datetime("Read Date", copy=False)
    # failure_type = fields.Selection(
    #     selection=[
    #         ("SMTP", "Connection failed (outgoing mail server problem)"),
    #         ("RECIPIENT", "Invalid email address"),
    #         ("BOUNCE", "Email address rejected by destination"),
    #         ("UNKNOWN", "Unknown error"),
    #     ],
    #     string="Failure type",
    # )
    failure_reason = fields.Text("Failure reason", copy=False)

    _sql_constraints = [
        # email notification;: partner is required
        (
            "notification_partner_required",
            "CHECK(notification_type NOT IN ('email', 'inbox') OR res_partner_id IS NOT NULL)",
            "Customer is required for inbox / email notification",
        ),
    ]

# -*- coding: utf-8 -*-

import logging
from ast import literal_eval
from odoo import api, fields, models, tools, _

_logger = logging.getLogger(__name__)

MASS_MESSAGING_BUSINESS_MODELS = [
    "crm.lead",
    "event.registration",
    "hr.employee",
    "hr.employee.category",
    "hr.department",
    "res.partner",
    "event.track",
    "sale.order",
    "mailing.list",
    "mailing.contact",
]


class MassWecomMessageing(models.Model):
    _name = "wecom.mass_messaging"
    _description = "Mass Messaging"
    _inherit = ["mail.thread", "mail.activity.mixin", "mail.render.mixin"]
    _order = "sent_date DESC"
    _inherits = {"utm.source": "source_id"}
    _rec_name = "subject"

    active = fields.Boolean(default=True, tracking=True)
    subject = fields.Char(
        "Subject", help="Subject of your Mailing", required=True, translate=True
    )
    preview = fields.Char(
        "Preview",
        translate=True,
        help="Catchy preview sentence that encourages recipients to open this email.\n"
        "In most inboxes, this is displayed next to the subject.\n"
        "Keep it empty if you prefer the first characters of your email content to appear instead.",
    )
    email_from = fields.Char(
        string="Send From",
        required=True,
        default=lambda self: self.env.user.email_formatted,
    )
    sent_date = fields.Datetime(string="Sent Date", copy=False)
    schedule_date = fields.Datetime(string="Scheduled for", tracking=True)
    # 不要翻译 'body_arch', 翻译仅在 'body_html' 上
    body_arch = fields.Html(string="Body", translate=False)
    body_html = fields.Html(
        string="Body converted to be sent by mail", sanitize_attributes=False
    )
    # attachment_ids = fields.Many2many(
    #     "ir.attachment",
    #     "mass_mailing_ir_attachments_rel",
    #     "mass_mailing_id",
    #     "attachment_id",
    #     string="Attachments",
    # )
    keep_archives = fields.Boolean(string="Keep Archives")
    campaign_id = fields.Many2one("utm.campaign", string="UTM Campaign", index=True)
    source_id = fields.Many2one(
        "utm.source",
        string="Source",
        required=True,
        ondelete="cascade",
        help="This is the link source, e.g. Search Engine, another domain, or name of email list",
    )
    # medium_id = fields.Many2one(
    #     "utm.medium",
    #     string="Medium",
    #     compute="_compute_medium_id",
    #     readonly=False,
    #     store=True,
    #     help="UTM Medium: delivery method (email, sms, ...)",
    # )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("in_queue", "In Queue"),
            ("sending", "Sending"),
            ("done", "Sent"),
        ],
        string="Status",
        required=True,
        tracking=True,
        copy=False,
        default="draft",
        group_expand="_group_expand_states",
    )
    color = fields.Integer(string="Color Index")
    user_id = fields.Many2one(
        "res.users",
        string="Responsible",
        tracking=True,
        default=lambda self: self.env.user,
    )
    # mailing options
    mailing_type = fields.Selection(
        [("mail", "Email")], string="Mailing Type", default="mail", required=True
    )
    # reply_to_mode = fields.Selection(
    #     [("thread", "Recipient Followers"), ("email", "Specified Email Address")],
    #     string="Reply-To Mode",
    #     compute="_compute_reply_to_mode",
    #     readonly=False,
    #     store=True,
    #     help="Thread: replies go to target document. Email: replies are routed to a given email.",
    # )
    # reply_to = fields.Char(
    #     string="Reply To",
    #     compute="_compute_reply_to",
    #     readonly=False,
    #     store=True,
    #     help="Preferred Reply-To Address",
    # )
    # recipients
    # mailing_model_real = fields.Char(
    #     string="Recipients Real Model", compute="_compute_model"
    # )
    # mailing_model_id = fields.Many2one(
    #     "ir.model",
    #     string="Recipients Model",
    #     ondelete="cascade",
    #     required=True,
    #     domain=[("model", "in", MASS_MESSAGING_BUSINESS_MODELS)],
    #     default=lambda self: self.env.ref("mass_mailing.model_mailing_list").id,
    # )
    # mailing_model_name = fields.Char(
    #     string="Recipients Model Name",
    #     related="mailing_model_id.model",
    #     readonly=True,
    #     related_sudo=True,
    # )
    # mailing_domain = fields.Char(
    #     string="Domain", compute="_compute_mailing_domain", readonly=False, store=True
    # )
    # mail_server_id = fields.Many2one(
    #     "ir.mail_server",
    #     string="Mail Server",
    #     default=_get_default_mail_server_id,
    #     help="Use a specific mail server in priority. Otherwise Odoo relies on the first outgoing mail server available (based on their sequencing) as it does for normal mails.",
    # )
    # contact_list_ids = fields.Many2many(
    #     "mailing.list", "mail_mass_mailing_list_rel", string="Mailing Lists"
    # )
    contact_ab_pc = fields.Integer(
        string="A/B Testing percentage",
        help="Percentage of the contacts that will be mailed. Recipients will be taken randomly.",
        default=100,
    )
    unique_ab_testing = fields.Boolean(
        string="Allow A/B Testing",
        default=False,
        help="If checked, recipients will be mailed only once for the whole campaign. "
        "This lets you send different mailings to randomly selected recipients and test "
        "the effectiveness of the mailings, without causing duplicate messages.",
    )
    kpi_mail_required = fields.Boolean("KPI mail required", copy=False)
    # statistics data
    # mailing_trace_ids = fields.One2many(
    #     "mailing.trace", "mass_mailing_id", string="Emails Statistics"
    # )
    # total = fields.Integer(compute="_compute_total")
    # scheduled = fields.Integer(compute="_compute_statistics")
    # expected = fields.Integer(compute="_compute_statistics")
    # ignored = fields.Integer(compute="_compute_statistics")
    # sent = fields.Integer(compute="_compute_statistics")
    # delivered = fields.Integer(compute="_compute_statistics")
    # opened = fields.Integer(compute="_compute_statistics")
    # clicked = fields.Integer(compute="_compute_statistics")
    # replied = fields.Integer(compute="_compute_statistics")
    # bounced = fields.Integer(compute="_compute_statistics")
    # failed = fields.Integer(compute="_compute_statistics")
    # received_ratio = fields.Integer(
    #     compute="_compute_statistics", string="Received Ratio"
    # )
    # opened_ratio = fields.Integer(compute="_compute_statistics", string="Opened Ratio")
    # replied_ratio = fields.Integer(
    #     compute="_compute_statistics", string="Replied Ratio"
    # )
    # bounced_ratio = fields.Integer(
    #     compute="_compute_statistics", string="Bounced Ratio"
    # )
    # clicks_ratio = fields.Integer(
    #     compute="_compute_clicks_ratio", string="Number of Clicks"
    # )
    # next_departure = fields.Datetime(
    #     compute="_compute_next_departure", string="Scheduled date"
    # )

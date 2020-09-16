# -*- coding: utf-8 -*-

from ...wxwork_api.CorpApi import *


import babel
import base64
import copy
import datetime
import dateutil.relativedelta as relativedelta
import functools
import logging

from werkzeug import urls

from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class MessageTemplate(models.Model):
    "Templates for Enterprise WeChat Message"
    _name = "wxwork.message.template"
    _description = "Enterprise WeChat Message Template"
    _order = "name"

    name = fields.Char("Name")
    model_id = fields.Many2one(
        "ir.model",
        "Applies to",
        help="The type of document this template can be used with",
    )
    model = fields.Char(
        "Related Document Model",
        related="model_id.model",
        index=True,
        store=True,
        readonly=True,
    )
    lang = fields.Char(
        "Language",
        help="Optional translation language (ISO code) to select when sending out an message. "
        "If not set, the english version will be used. "
        "This should usually be a placeholder expression "
        "that provides the appropriate language, e.g. "
        "${object.partner_id.lang}.",
        placeholder="${object.partner_id.lang}",
    )
    user_signature = fields.Boolean(
        "Add Signature",
        help="If checked, the user's signature will be appended to the text version "
        "of the message",
    )
    subject = fields.Char(
        "Subject", translate=True, help="Subject (placeholders may be used here)"
    )
    message_from = fields.Char(
        "From",
        help="Sender address (placeholders may be used here). If not set, the default "
        "value will be the author's message alias if configured, or message address.",
    )
    use_default_to = fields.Boolean(
        "Default recipients",
        help="Default recipients of the record:\n"
        "- partner (using id on a partner or the partner_id field) OR\n"
        "- message (using message_from or message field)",
    )
    message_to = fields.Char(
        "To (messages)",
        help="Comma-separated recipient addresses (placeholders may be used here)",
    )
    partner_to = fields.Char(
        "To (Partners)",
        help="Comma-separated ids of recipient partners (placeholders may be used here)",
    )
    message_cc = fields.Char(
        "Cc", help="Carbon copy recipients (placeholders may be used here)"
    )
    reply_to = fields.Char(
        "Reply-To", help="Preferred response address (placeholders may be used here)"
    )
    mail_server_id = fields.Many2one(
        "ir.mail_server",
        "Outgoing Mail Server",
        readonly=False,
        help="Optional preferred server for outgoing mails. If not set, the highest "
        "priority one will be used.",
    )
    body_html = fields.Html("Body", translate=True, sanitize=False)
    report_name = fields.Char(
        "Report Filename",
        translate=True,
        help="Name to use for the generated report file (may contain placeholders)\n"
        "The extension can be omitted and will then come from the report type.",
    )
    report_template = fields.Many2one(
        "ir.actions.report", "Optional report to print and attach"
    )
    ref_ir_act_window = fields.Many2one(
        "ir.actions.act_window",
        "Sidebar action",
        readonly=True,
        copy=False,
        help="Sidebar action to make this template available on records "
        "of the related document model",
    )
    # attachment_ids = fields.Many2many(
    #     "ir.attachment",
    #     "message_template_attachment_rel",
    #     "message_template_id",
    #     "attachment_id",
    #     "Attachments",
    #     help="You may attach files to this template, to be added to all "
    #     "messages created from this template",
    # )
    auto_delete = fields.Boolean(
        "Auto Delete",
        default=True,
        help="Permanently delete this message after sending it, to save space",
    )

    # Fake fields used to implement the placeholder assistant
    model_object_field = fields.Many2one(
        "ir.model.fields",
        string="Field",
        help="Select target field from the related document model.\n"
        "If it is a relationship field you will be able to select "
        "a target field at the destination of the relationship.",
    )
    sub_object = fields.Many2one(
        "ir.model",
        "Sub-model",
        readonly=True,
        help="When a relationship field is selected as first field, "
        "this field shows the document model the relationship goes to.",
    )
    sub_model_object_field = fields.Many2one(
        "ir.model.fields",
        "Sub-field",
        help="When a relationship field is selected as first field, "
        "this field lets you select the target field within the "
        "destination document model (sub-model).",
    )
    null_value = fields.Char(
        "Default Value", help="Optional value to use if the target field is empty"
    )
    copyvalue = fields.Char(
        "Placeholder Expression",
        help="Final placeholder expression, to be copy-pasted in the desired template field.",
    )
    scheduled_date = fields.Char(
        "Scheduled Date",
        help="If set, the queue manager will send the message after the date. If not set, the message will be send as soon as possible. Jinja2 placeholders may be used.",
    )

    # 以下为企业微信独有字段

    msgtype = fields.Selection([
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
        'Message type', required=True, default='markdown',
        help="Policy on how to handle Chatter notifications:\n"
             "- Handle by Emails: notifications are sent to your email address\n"
             "- Handle in Odoo: notifications appear in your Odoo Inbox")
    # safe = fields.Boolean("保密消息", default=False)

    # title = fields.Char("标题", size=128, help="视频消息的标题，不超过128个字节，超过会自动截断")
    # description = fields.Char("描述", size=512, help="描述，不超过512个字节，超过会自动截断")
    # content = fields.Text("消息主体", help="最长不超过2048个字节，超过将截断")
    # url = fields.Char("点击后跳转的链接", help="点击后跳转的链接")
    # picurl = fields.Char(
    #     "图片链接", help="图文消息的图片链接，支持JPG、PNG格式，较好的效果为大图 1068*455，小图150*150。"
    # )
    # btntxt = fields.Char("按钮文字", size=4, help="按钮文字。 默认为“详情”， 不超过4个文字，超过自动截断。")

    # enable_id_trans = fields.Boolean(
    #     string="开启id转译", help="0表示否，1表示是，默认0", default=False
    # )
    # enable_duplicate_check = fields.Boolean(
    #     string="表示是否开启重复消息检查，", help="表示是否开启id转译，0表示否，1表示是，默认0", default=False
    # )
    # duplicate_check_interval = fields.Integer(
    #     string="重复消息检查的时间间隔", help="表示是否重复消息检查的时间间隔，默认1800s，最大不超过4小时", default=1800
    # )

    @api.model
    def copy_mail_template(self):
        templates = self.sudo().env["mail.template"].search([])
        for template in templates:
            # print(template.name)
            self.create({
                "name": template.name,
                "model_id": template.model_id.id,
                # "model": template.model,
                # "lang": template.lang,
                # "user_signature": template.user_signature,
                # "subject": template.subject,
                # "message_from": template.email_from,
                # "use_default_to": template.use_default_to,
                # "message_to": template.email_to,
                # "partner_to": template.partner_to,
                # "message_cc": template.email_cc,
                # "reply_to": template.reply_to,
                # "mail_server_id": template.mail_server_id,
                # "body_html": template.body_html,
                # "report_name": template.report_name,
                # "report_template": template.report_template,


                # "ref_ir_act_window": template.ref_ir_act_window,
                # "auto_delete": template.auto_delete,
                # "sub_object": template.sub_object,
                # "sub_model_object_field": template.sub_model_object_field,
                # "null_value": template.null_value,
                # "copyvalue": template.copyvalue,
                # "scheduled_date": template.scheduled_date,
                # "msgtype": "markdown",
            })

        return True

    @api.onchange('model_id')
    def onchange_model_id(self):
        # TDE CLEANME: should'nt it be a stored related ?
        if self.model_id:
            self.model = self.model_id.model
        else:
            self.model = False

    @api.onchange('model_object_field', 'sub_model_object_field', 'null_value')
    def onchange_sub_model_object_value_field(self):
        if self.model_object_field:
            if self.model_object_field.ttype in ['many2one', 'one2many', 'many2many']:
                model = self.env['ir.model']._get(
                    self.model_object_field.relation)
                if model:
                    self.sub_object = model.id
                    self.copyvalue = self.build_expression(
                        self.model_object_field.name, self.sub_model_object_field and self.sub_model_object_field.name or False, self.null_value or False)
            else:
                self.sub_object = False
                self.sub_model_object_field = False
                self.copyvalue = self.build_expression(
                    self.model_object_field.name, False, self.null_value or False)
        else:
            self.sub_object = False
            self.copyvalue = False
            self.sub_model_object_field = False
            self.null_value = False

    def unlink(self):
        self.unlink_action()
        return super(MessageTemplate, self).unlink()

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {},
                       name=_("%s (copy)") % self.name)
        return super(MessageTemplate, self).copy(default=default)

    def unlink_action(self):
        for template in self:
            if template.ref_ir_act_window:
                template.ref_ir_act_window.unlink()
        return True

    def create_action(self):
        ActWindow = self.env['ir.actions.act_window']
        view = self.env.ref('mail.email_compose_message_wizard_form')

        for template in self:
            button_name = _('Send Mail (%s)') % template.name
            action = ActWindow.create({
                'name': button_name,
                'type': 'ir.actions.act_window',
                'res_model': 'mail.compose.message',
                'context': "{'default_composition_mode': 'mass_mail', 'default_template_id' : %d, 'default_use_template': True}" % (template.id),
                'view_mode': 'form,tree',
                'view_id': view.id,
                'target': 'new',
                'binding_model_id': template.model_id.id,
            })
            template.write({'ref_ir_act_window': action.id})

        return True

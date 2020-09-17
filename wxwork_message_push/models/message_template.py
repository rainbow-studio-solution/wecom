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


def format_date(env, date, pattern=False, lang_code=False):
    try:
        return tools.format_date(env, date, date_format=pattern, lang_code=lang_code)
    except babel.core.UnknownLocaleError:
        return date


def format_datetime(env, dt, tz=False, dt_format="medium", lang_code=False):
    try:
        return tools.format_datetime(
            env, dt, tz=tz, dt_format=dt_format, lang_code=lang_code
        )
    except babel.core.UnknownLocaleError:
        return dt


try:
    # We use a jinja2 sandboxed environment to render mako templates.
    # Note that the rendering does not cover all the mako syntax, in particular
    # arbitrary Python statements are not accepted, and not all expressions are
    # allowed: only "public" attributes (not starting with '_') of objects may
    # be accessed.
    # This is done on purpose: it prevents incidental or malicious execution of
    # Python code that may break the security of the server.
    from jinja2.sandbox import SandboxedEnvironment

    mako_template_env = SandboxedEnvironment(
        block_start_string="<%",
        block_end_string="%>",
        variable_start_string="${",
        variable_end_string="}",
        comment_start_string="<%doc>",
        comment_end_string="</%doc>",
        line_statement_prefix="%",
        line_comment_prefix="##",
        trim_blocks=True,  # do not output newline after blocks
        autoescape=True,  # XML/HTML automatic escaping
    )
    mako_template_env.globals.update(
        {
            "str": str,
            "quote": urls.url_quote,
            "urlencode": urls.url_encode,
            "datetime": datetime,
            "len": len,
            "abs": abs,
            "min": min,
            "max": max,
            "sum": sum,
            "filter": filter,
            "reduce": functools.reduce,
            "map": map,
            "round": round,
            # dateutil.relativedelta is an old-style class and cannot be directly
            # instanciated wihtin a jinja2 expression, so a lambda "proxy" is
            # is needed, apparently.
            "relativedelta": lambda *a, **kw: relativedelta.relativedelta(*a, **kw),
        }
    )
    mako_safe_template_env = copy.copy(mako_template_env)
    mako_safe_template_env.autoescape = False
except ImportError:
    _logger.warning("jinja2 not available, templating features will not work!")


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
    attachment_ids = fields.Many2many(
        "ir.attachment",
        "message_template_attachment_rel",
        "message_template_id",
        "attachment_id",
        "Attachments",
        help="You may attach files to this template, to be added to all "
        "messages created from this template",
    )
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
        "Message type",
        required=True,
        default="markdown",
        help="Policy on how to handle Chatter notifications:\n"
        "- Handle by Emails: notifications are sent to your email address\n"
        "- Handle in Odoo: notifications appear in your Odoo Inbox",
    )
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
            message = self.search(
                [("name", "=", template.name)],
                limit=1,
            )
            if len(message) > 0:
                pass
            else:
                self.create(
                    {
                        "name": template.name,
                        "model_id": template.model_id.id,
                        # "model": template.model,
                        "lang": template.lang,
                        "user_signature": template.user_signature,
                        "subject": template.subject,
                        "message_from": template.email_from,
                        "use_default_to": template.use_default_to,
                        "message_to": template.email_to,
                        "partner_to": template.partner_to,
                        "message_cc": template.email_cc,
                        "reply_to": template.reply_to,
                        # "mail_server_id": template.mail_server_id,
                        "body_html": template.body_html,
                        "report_name": template.report_name,
                        "report_template": template.report_template.id,
                        "ref_ir_act_window": template.ref_ir_act_window.id,
                        "attachment_ids": template.attachment_ids.id,
                        "auto_delete": template.auto_delete,
                        "model_object_field": template.model_object_field.id,
                        "sub_object": template.sub_object.id,
                        "sub_model_object_field": template.sub_model_object_field.id,
                        "null_value": template.null_value,
                        "copyvalue": template.copyvalue,
                        "scheduled_date": template.scheduled_date,
                        "msgtype": "textcard",
                    }
                )

        return True

    @api.onchange("model_id")
    def onchange_model_id(self):
        # TDE CLEANME: should'nt it be a stored related ?
        if self.model_id:
            self.model = self.model_id.model
        else:
            self.model = False

    @api.onchange("model_object_field", "sub_model_object_field", "null_value")
    def onchange_sub_model_object_value_field(self):
        if self.model_object_field:
            if self.model_object_field.ttype in ["many2one", "one2many", "many2many"]:
                model = self.env["ir.model"]._get(self.model_object_field.relation)
                if model:
                    self.sub_object = model.id
                    self.copyvalue = self.build_expression(
                        self.model_object_field.name,
                        self.sub_model_object_field
                        and self.sub_model_object_field.name
                        or False,
                        self.null_value or False,
                    )
            else:
                self.sub_object = False
                self.sub_model_object_field = False
                self.copyvalue = self.build_expression(
                    self.model_object_field.name, False, self.null_value or False
                )
        else:
            self.sub_object = False
            self.copyvalue = False
            self.sub_model_object_field = False
            self.null_value = False

    def unlink(self):
        self.unlink_action()
        return super(MessageTemplate, self).unlink()

    @api.returns("self", lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {}, name=_("%s (copy)") % self.name)
        return super(MessageTemplate, self).copy(default=default)

    def unlink_action(self):
        for template in self:
            if template.ref_ir_act_window:
                template.ref_ir_act_window.unlink()
        return True

    def create_action(self):
        ActWindow = self.env["ir.actions.act_window"]
        view = self.env.ref("mail.email_compose_message_wizard_form")

        for template in self:
            button_name = _("Send Mail (%s)") % template.name
            action = ActWindow.create(
                {
                    "name": button_name,
                    "type": "ir.actions.act_window",
                    "res_model": "mail.compose.message",
                    "context": "{'default_composition_mode': 'mass_mail', 'default_template_id' : %d, 'default_use_template': True}"
                    % (template.id),
                    "view_mode": "form,tree",
                    "view_id": view.id,
                    "target": "new",
                    "binding_model_id": template.model_id.id,
                }
            )
            template.write({"ref_ir_act_window": action.id})

        return True

    def generate_message(self, res_ids, fields=None):
        """Generates an email from the template for given the given model based on
        records given by res_ids.

        :param res_id: id of the record to use for rendering the template (model
                       is taken from template definition)
        :returns: a dict containing all relevant fields for creating a new
                  mail.mail entry, with one extra key ``attachments``, in the
                  format [(report_name, data)] where data is base64 encoded.
        """
        self.ensure_one()
        multi_mode = True
        if isinstance(res_ids, int):
            res_ids = [res_ids]
            multi_mode = False
        if fields is None:
            fields = [
                "subject",
                "body_html",
                "message_from",
                "message_to",
                "partner_to",
                "message_cc",
                "reply_to",
                "scheduled_date",
            ]

        res_ids_to_templates = self.get_message_template(res_ids)

        # templates: res_id -> template; template -> res_ids
        templates_to_res_ids = {}
        for res_id, template in res_ids_to_templates.items():
            templates_to_res_ids.setdefault(template, []).append(res_id)

        results = dict()
        for template, template_res_ids in templates_to_res_ids.items():
            Template = self.env["mail.template"]
            # generate fields value for all res_ids linked to the current template
            if template.lang:
                Template = Template.with_context(lang=template._context.get("lang"))
            for field in fields:
                Template = Template.with_context(safe=field in {"subject"})
                generated_field_values = Template._render_template(
                    getattr(template, field),
                    template.model,
                    template_res_ids,
                    post_process=(field == "body_html"),
                )
                for res_id, field_value in generated_field_values.items():
                    results.setdefault(res_id, dict())[field] = field_value
            # compute recipients
            if any(
                field in fields for field in ["message_to", "partner_to", "message_cc"]
            ):
                results = template.generate_recipients(results, template_res_ids)
            # update values for all res_ids
            for res_id in template_res_ids:
                values = results[res_id]
                # body: add user signature, sanitize
                if "body_html" in fields and template.user_signature:
                    signature = self.env.user.signature
                    if signature:
                        values["body_html"] = tools.append_content_to_html(
                            values["body_html"], signature, plaintext=False
                        )
                if values.get("body_html"):
                    values["body"] = tools.html_sanitize(values["body_html"])
                # technical settings
                values.update(
                    mail_server_id=template.mail_server_id.id or False,
                    auto_delete=template.auto_delete,
                    model=template.model,
                    res_id=res_id or False,
                    attachment_ids=[attach.id for attach in template.attachment_ids],
                )

            # Add report in attachments: generate once for all template_res_ids
            if template.report_template:
                for res_id in template_res_ids:
                    attachments = []
                    report_name = self._render_template(
                        template.report_name, template.model, res_id
                    )
                    report = template.report_template
                    report_service = report.report_name

                    if report.report_type in ["qweb-html", "qweb-pdf"]:
                        result, format = report.render_qweb_pdf([res_id])
                    else:
                        res = report.render([res_id])
                        if not res:
                            raise UserError(
                                _("Unsupported report type %s found.")
                                % report.report_type
                            )
                        result, format = res

                    # TODO in trunk, change return format to binary to match message_post expected format
                    result = base64.b64encode(result)
                    if not report_name:
                        report_name = "report." + report_service
                    ext = "." + format
                    if not report_name.endswith(ext):
                        report_name += ext
                    attachments.append((report_name, result))
                    results[res_id]["attachments"] = attachments

        return multi_mode and results or results[res_ids[0]]

    # ----------------------------------------
    # EMAIL
    # ----------------------------------------

    def send_message(
        self,
        res_id,
        force_send=False,
        raise_exception=False,
        message_values=None,
        notif_layout=False,
    ):
        """Generates a new mail.mail. Template is rendered on record given by
        res_id and model coming from template.

        :param int res_id: id of the record to render the template
        :param bool force_send: send email immediately; otherwise use the mail
            queue (recommended);
        :param dict message_values: update generated mail with those values to further
            customize the mail;
        :param str notif_layout: optional notification layout to encapsulate the
            generated email;
        :returns: id of the mail.mail that was created"""
        self.ensure_one()
        Mail = self.env["mail.mail"]
        Attachment = self.env[
            "ir.attachment"
        ]  # TDE FIXME: should remove default_type from context

        # create a mail_mail based on values, without attachments
        values = self.generate_email(res_id)
        values["recipient_ids"] = [
            (4, pid) for pid in values.get("partner_ids", list())
        ]
        values["attachment_ids"] = [
            (4, aid) for aid in values.get("attachment_ids", list())
        ]
        values.update(message_values or {})
        attachment_ids = values.pop("attachment_ids", [])
        attachments = values.pop("attachments", [])
        # add a protection against void message_from
        if "message_from" in values and not values.get("message_from"):
            values.pop("message_from")
        # encapsulate body
        if notif_layout and values["body_html"]:
            try:
                template = self.env.ref(notif_layout, raise_if_not_found=True)
            except ValueError:
                _logger.warning(
                    "QWeb template %s not found when sending template %s. Sending without layouting."
                    % (notif_layout, self.name)
                )
            else:
                record = self.env[self.model].browse(res_id)
                lang = self._render_template(self.lang, self.model, res_id)
                model = self.env["ir.model"]._get(record._name)
                if lang:
                    template = template.with_context(lang=lang)
                    model = model.with_context(lang=lang)
                template_ctx = {
                    "message": self.env["mail.message"]
                    .sudo()
                    .new(
                        dict(body=values["body_html"], record_name=record.display_name)
                    ),
                    "model_description": model.display_name,
                    "company": "company_id" in record
                    and record["company_id"]
                    or self.env.company,
                    "record": record,
                }
                body = template.render(
                    template_ctx, engine="ir.qweb", minimal_qcontext=True
                )
                values["body_html"] = self.env["mail.thread"]._replace_local_links(body)
        mail = Mail.create(values)

        # manage attachments
        for attachment in attachments:
            attachment_data = {
                "name": attachment[0],
                "datas": attachment[1],
                "type": "binary",
                "res_model": "mail.message",
                "res_id": mail.mail_message_id.id,
            }
            attachment_ids.append((4, Attachment.create(attachment_data).id))
        if attachment_ids:
            mail.write({"attachment_ids": attachment_ids})

        if force_send:
            mail.send(raise_exception=raise_exception)
        return mail.id  # TDE CLEANME: return mail + api.returns ?

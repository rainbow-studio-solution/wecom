# -*- coding: utf-8 -*-

import base64
import logging


from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError
import html2text

_logger = logging.getLogger(__name__)


class MailTemplate(models.Model):
    _inherit = "mail.template"

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
        default="markdown",
        help="Policy on how to handle Chatter notifications:\n"
        "- Handle by Emails: notifications are sent to your email address\n"
        "- Handle in Odoo: notifications appear in your Odoo Inbox",
    )
    safe = fields.Boolean(string="Confidential message", default=False)
    wxwork_body_html = fields.Html(
        "Enterprise WeChat Message Body", translate=True, sanitize=False
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
    def copy_body_html(self):
        for template in self.search([]):
            if not template.wxwork_body_html:
                # 判断企业微信消息模板为空
                template.wxwork_body_html = self.html2text_handle(template.body_html)

    def html2text_handle(self, html):
        # 转换markdown格式
        if bool(html):
            return html2text.html2text(html)
        else:
            return None

    def send_mail(
        self,
        res_id,
        force_send=False,
        raise_exception=False,
        email_values=None,
        notif_layout=False,
    ):
        if self.env["res.users"].browse(res_id).notification_type == "wxwork":
            # res_id 是用户id
            # 拦截 用户通知类型为企业微信的发送方式
            values = self.generate_message(
                res_id,
                [
                    "subject",
                    "wxwork_body_html",
                    "email_from",
                    "email_to",
                    "partner_to",
                    "email_cc",
                    "reply_to",
                    "scheduled_date",
                ],
            )
            print(values)

        return super(MailTemplate, self).send_mail(
            res_id,
            force_send=False,
            raise_exception=False,
            email_values=None,
            notif_layout=False,
        )

    def generate_message(self, res_ids, fields):
        self.ensure_one()
        multi_mode = True
        if isinstance(res_ids, int):
            res_ids = [res_ids]
            multi_mode = False

        results = dict()
        for lang, (template, template_res_ids) in self._classify_per_lang(
            res_ids
        ).items():
            for field in fields:
                template = template.with_context(safe=(field == "subject"))
                generated_field_values = template._render_field(
                    field, template_res_ids, post_process=(field == "wxwork_body_html")
                )
                for res_id, field_value in generated_field_values.items():
                    results.setdefault(res_id, dict())[field] = field_value
            # compute recipients
            if any(field in fields for field in ["email_to", "partner_to", "email_cc"]):
                results = template.generate_recipients(results, template_res_ids)
            # update values for all res_ids
            for res_id in template_res_ids:
                values = results[res_id]
                if values.get("wxwork_body_html"):
                    values["body"] = tools.html_sanitize(values["wxwork_body_html"])
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
                    report_name = self._render_field("report_name", [res_id])[res_id]
                    report = template.report_template
                    report_service = report.report_name

                    if report.report_type in ["qweb-html", "qweb-pdf"]:
                        result, format = report._render_qweb_pdf([res_id])
                    else:
                        res = report._render([res_id])
                        if not res:
                            raise UserError(
                                _(
                                    "Unsupported report type %s found.",
                                    report.report_type,
                                )
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
        return super(MailTemplate, self).generate_email(res_ids, fields)

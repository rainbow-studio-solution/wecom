# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError


class MailTemplatePreview(models.TransientModel):
    _inherit = ["mail.template.preview"]
    # _name = "wecom.message.template.preview"
    # _description = "WeCom message Template Preview"

    _MAIL_TEMPLATE_FIELDS = [
        "subject",
        "body_html",
        "email_from",
        "email_to",
        "email_cc",
        "reply_to",
        "msgtype",
        "message_to_user",
        "message_to_party",
        "message_to_tag",
        "body_json",
        "body_html",
        "body_markdown",
        "scheduled_date",
        "attachment_ids",
    ]

    msgtype = fields.Char(
        string="Message type", compute="_compute_wecom_message_template_fields"
    )

    message_to_user = fields.Char(string="To Users", help="Message recipients (users)",)
    message_to_party = fields.Char(
        string="To Departments", help="Message recipients (departments)",
    )
    message_to_tag = fields.Char(string="To Tags", help="Message recipients (tags)",)

    body_html = fields.Html(
        "Html Body", compute="_compute_wecom_message_template_fields"
    )
    body_json = fields.Text(
        "Json Body", compute="_compute_wecom_message_template_fields"
    )
    body_markdown = fields.Text(
        "Markdown Body", compute="_compute_wecom_message_template_fields"
    )

    @api.depends("lang", "resource_ref")
    def _compute_wecom_message_template_fields(self):
        """ Preview the mail template (body, subject, ...) depending of the language and
        the record reference, more precisely the record id for the defined model of the mail template.
        If no record id is selectable/set, the jinja placeholders won't be replace in the display information. """
        copy_depends_values = {"lang": self.lang}
        mail_template = self.mail_template_id.with_context(lang=self.lang)
        try:
            if not self.resource_ref:
                self._set_mail_attributes()
            else:
                copy_depends_values["resource_ref"] = "%s,%s" % (
                    self.resource_ref._name,
                    self.resource_ref.id,
                )
                mail_values = mail_template.with_context(
                    template_preview_lang=self.lang
                ).generate_wecom_message(
                    self.resource_ref.id, self._MAIL_TEMPLATE_FIELDS
                )
                self._set_mail_attributes(values=mail_values)
            self.error_msg = False
        except UserError as user_error:
            self._set_mail_attributes()
            self.error_msg = user_error.args[0]
        finally:
            # Avoid to be change by a invalidate_cache call (in generate_mail), e.g. Quotation / Order report
            for key, value in copy_depends_values.items():
                self[key] = value

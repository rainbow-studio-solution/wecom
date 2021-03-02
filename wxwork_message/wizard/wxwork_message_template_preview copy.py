# -*- coding: utf-8 -*-

from odoo import api, fields, models


class WxWorkMessageTemplatePreview(models.TransientModel):
    _inherit = ["mail.template.preview"]
    # _name = "wxwork.message.template.preview"
    # _description = "Enterprise WeChat message Template Preview"

    @api.model
    def _selection_target_model(self):
        models = self.env["ir.model"].search([])
        return [(model.model, model.name) for model in models]

    @api.model
    def _selection_languages(self):
        return self.env["res.lang"].get_installed()

    @api.model
    def default_get(self, fields):
        result = super(WxWorkMessageTemplatePreview, self).default_get(fields)
        wxwork_message_template_id = self.env.context.get(
            "default_wxwork_message_template_id"
        )
        if not wxwork_message_template_id or "resource_ref" not in fields:
            return result
        wxwork_message_template = self.env["wxwork.message.template"].browse(
            wxwork_message_template_id
        )
        res = self.env[wxwork_message_template.model_id.model].search([], limit=1)
        if res:
            result["resource_ref"] = "%s,%s" % (
                wxwork_message_template.model_id.model,
                res.id,
            )
        return result

    wxwork_message_template_id = fields.Many2one(
        "wxwork.message.template", required=True, ondelete="cascade"
    )
    lang = fields.Selection(_selection_languages, string="Template Preview Language")
    model_id = fields.Many2one(
        "ir.model", related="wxwork_message_template_id.model_id"
    )
    msgtype = fields.Char(
        string="Message type", compute="_compute_wxwork_message_template_msgtype_fields"
    )
    body_text = fields.Text(
        "Body", compute="_compute_wxwork_message_template_text_fields"
    )
    body_html = fields.Html(
        "Body", compute="_compute_wxwork_message_template_html_fields"
    )
    resource_ref = fields.Reference(
        string="Record reference", selection="_selection_target_model"
    )
    no_record = fields.Boolean("No Record", compute="_compute_no_record")

    @api.depends("model_id")
    def _compute_no_record(self):
        for preview in self:
            preview.no_record = (
                (self.env[preview.model_id.model].search_count([]) == 0)
                if preview.model_id
                else True
            )

    @api.depends("lang", "resource_ref")
    def _compute_wxwork_message_template_text_fields(self):
        for wizard in self:
            if wizard.wxwork_message_template_id and wizard.resource_ref:
                wizard.body_text = wizard.wxwork_message_template_id._render_field(
                    "body_text", [wizard.resource_ref.id], set_lang=wizard.lang
                )[wizard.resource_ref.id]
            else:
                wizard.body_text = wizard.wxwork_message_template_id.body_text

    @api.depends("lang", "resource_ref")
    def _compute_wxwork_message_template_html_fields(self):
        for wizard in self:
            if wizard.wxwork_message_template_id and wizard.resource_ref:
                wizard.body_html = wizard.wxwork_message_template_id._render_field(
                    "body_html", [wizard.resource_ref.id], set_lang=wizard.lang
                )[wizard.resource_ref.id]
            else:
                wizard.body_html = wizard.wxwork_message_template_id.body_html

    @api.depends("lang", "resource_ref")
    def _compute_wxwork_message_template_msgtype_fields(self):
        for wizard in self:
            if wizard.wxwork_message_template_id and wizard.resource_ref:
                wizard.msgtype = wizard.wxwork_message_template_id._render_field(
                    "msgtype", [wizard.resource_ref.id], set_lang=wizard.lang
                )[wizard.resource_ref.id]
            else:
                wizard.msgtype = wizard.wxwork_message_template_id.msgtype


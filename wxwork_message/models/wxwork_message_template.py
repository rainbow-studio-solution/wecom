# -*- coding: utf-8 -*-

import base64
import logging
from ...wxwork_api.helper.common import Common
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class WxWorkMessageTemplate(models.Model):
    "Template for sending Enterprise WeChat message"
    _name = "wxwork.message.template"
    # _inherit = ["wxwork.message.render.mixin"]
    _inherit = ["mail.render.mixin"]
    _description = "Enterprise WeChat message Templates"
    _order = "name"

    @api.model
    def default_get(self, fields):
        res = super(WxWorkMessageTemplate, self).default_get(fields)
        if (
            not fields
            or "model_id" in fields
            and not res.get("model_id")
            and res.get("model")
        ):
            res["model_id"] = self.env["ir.model"]._get(res["model"]).id
        return res

    name = fields.Char("Name")
    subject = fields.Char("Subject", translate=True, help="主题（此处可以使用占位符） ")
    # model_id = fields.Many2one("ir.model", "Applies to", help="可以与该模板一起使用的文档类型",)
    model_id = fields.Many2one(
        "ir.model",
        string="Applies to",
        required=True,
        domain=["&", ("is_mail_thread_wxwork", "=", True), ("transient", "=", False)],
        help="可以与该模板一起使用的文档类型",
        ondelete="cascade",
    )
    model = fields.Char(
        "Related Document Model",
        related="model_id.model",
        index=True,
        store=True,
        readonly=True,
    )

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
    )

    email_to_all = fields.Boolean("To all members", readonly=True,)
    email_to_user = fields.Many2many(
        "hr.employee",
        string="To Employees",
        domain="[('active', '=', True), ('is_wxwork_employee', '=', True)]",
        help="Message recipients (users)",
    )
    email_to_party = fields.Many2many(
        "hr.department",
        string="To Departments",
        domain="[('active', '=', True), ('is_wxwork_department', '=', True)]",
        help="Message recipients (departments)",
    )
    email_to_tag = fields.Many2many(
        "hr.employee.category",
        # "employee_category_rel",
        # "emp_id",
        # "category_id",
        string="To Tags",
        domain="[('is_wxwork_category', '=', True)]",
        help="Message recipients (tags)",
    )

    # content
    body = fields.Char("Body", translate=True, required=True)
    # 用于创建上下文操作（与电子邮件模板相同）
    sidebar_action_id = fields.Many2one(
        "ir.actions.act_window",
        "Sidebar action",
        readonly=True,
        copy=False,
        help="Sidebar action to make this template available on records "
        "of the related document model",
    )

    # options

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

    @api.returns("self", lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {}, name=_("%s (copy)", self.name))
        return super(WxWorkMessageTemplate, self).copy(default=default)

    def unlink(self):
        self.sudo().mapped("sidebar_action_id").unlink()
        return super(WxWorkMessageTemplate, self).unlink()

    def action_create_sidebar_action(self):
        ActWindow = self.env["ir.actions.act_window"]
        view = self.env.ref("sms.sms_composer_view_form")

        for template in self:
            button_name = _("Send SMS (%s)", template.name)
            action = ActWindow.create(
                {
                    "name": button_name,
                    "type": "ir.actions.act_window",
                    "res_model": "sms.composer",
                    # Add default_composition_mode to guess to determine if need to use mass or comment composer
                    "context": "{'default_template_id' : %d, 'sms_composition_mode': 'guess', 'default_res_ids': active_ids, 'default_res_id': active_id}"
                    % (template.id),
                    "view_mode": "form",
                    "view_id": view.id,
                    "target": "new",
                    "binding_model_id": template.model_id.id,
                }
            )
            template.write({"sidebar_action_id": action.id})
        return True

    def action_unlink_sidebar_action(self):
        for template in self:
            if template.sidebar_action_id:
                template.sidebar_action_id.unlink()
        return True

    # ------------------------------------------------------------
    # 企业微信消息 值的生成
    # ------------------------------------------------------------

    def generate_recipients(self, results, res_ids):
        """
        生成模板的收件人。 如果模板或上下文要求，则可以生成默认值而不是模板值。
        如果上下文中有要求，可以将电子邮件（email_to，email_cc）转换为合作伙伴。 
        """
        self.ensure_one()

        if self.use_default_to or self._context.get("tpl_force_default_to"):
            records = self.env[self.model].browse(res_ids).sudo()
            default_recipients = records._message_get_default_recipients()
            for res_id, recipients in default_recipients.items():
                results[res_id].pop("partner_to", None)
                results[res_id].update(recipients)

        records_company = None
        if (
            self._context.get("tpl_partners_only")
            and self.model
            and results
            and "company_id" in self.env[self.model]._fields
        ):
            records = self.env[self.model].browse(results.keys()).read(["company_id"])
            records_company = {
                rec["id"]: (rec["company_id"][0] if rec["company_id"] else None)
                for rec in records
            }

        for res_id, values in results.items():
            partner_ids = values.get("partner_ids", list())
            if self._context.get("tpl_partners_only"):
                mails = tools.email_split(
                    values.pop("message_email_to", "")
                ) + tools.email_split(values.pop("email_cc", ""))
                Partner = self.env["res.partner"]
                if records_company:
                    Partner = Partner.with_context(
                        default_company_id=records_company[res_id]
                    )
                for mail in mails:
                    partner = Partner.find_or_create(mail)
                    partner_ids.append(partner.id)
            partner_to = values.pop("partner_to", "")
            if partner_to:
                # placeholders could generate '', 3, 2 due to some empty field values
                tpl_partner_ids = [int(pid) for pid in partner_to.split(",") if pid]
                partner_ids += (
                    self.env["res.partner"].sudo().browse(tpl_partner_ids).exists().ids
                )

            results[res_id]["message_email_to"] = (
                self.env["res.users"].sudo().browse(res_ids).wxwork_id
            )
            results[res_id]["partner_ids"] = partner_ids
        return results

    def generate_message(self, res_ids, fields):
        """
        根据res_ids给定的记录，从给定给定模型的模板生成企业微信消息。 

        :param res_id: 用于呈现模板的记录的ID（模型来自模板定义） 
        :returns: 包含所有用于创建新 wxwork.mail 条目的所有相关字段的字典，带有一个额外的键``attachments``，格式为[(report_name, data)]，其中数据是base64编码的。 
        """
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
                    field, template_res_ids, post_process=(field == "body_html")
                )
                for res_id, field_value in generated_field_values.items():
                    results.setdefault(res_id, dict())[field] = field_value
            # 计算接收人
            if any(
                field in fields
                for field in ["message_email_to", "partner_to", "email_cc"]
            ):
                results = template.generate_recipients(results, template_res_ids)
            # 更新所有res_id的值
            for res_id in template_res_ids:
                values = results[res_id]
                if values.get("body_html"):
                    values["body"] = tools.html_sanitize(values["body_html"])
                # 技术设置
                values.update(
                    # mail_server_id=template.mail_server_id.id or False,
                    auto_delete=template.auto_delete,
                    model=template.model,
                    res_id=res_id or False,
                    attachment_ids=[attach.id for attach in template.attachment_ids],
                )

            # 在附件中添加报告：为所有template_res_ids生成一次
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

    # ------------------------------------------------------------
    # 消息
    # ------------------------------------------------------------

    def _send_check_access(self, res_ids):
        records = self.env[self.model].browse(res_ids)
        records.check_access_rights("read")
        records.check_access_rule("read")

    def send_message(
        self,
        res_id,
        force_send=False,
        raise_exception=False,
        email_values=None,
        notif_layout=False,
    ):
        """ 
        生成一个新的mail.mail。 模板在由res_id和来自模板的模型给定的记录中呈现。 

        :param int res_id: 渲染模板的记录的ID 
        :param bool force_send: 立即发送电子邮件； 否则使用邮件队列（推荐）； 
        :param dict email_values: 使用这些值更新生成的邮件，以进一步自定义邮件；
        :param str notif_layout: 可选的通知布局，用于封装生成的电子邮件； 
        :returns: 创建的mail.mail的ID 
        """

        # 仅在访问相关文档时才授予对 send_message 的访问权限
        self.ensure_one()
        self._send_check_access([res_id])

        Attachment = self.env[
            "ir.attachment"
        ]  # TDE FIXME: should remove default_type from context

        # 根据值创建一个mail_mail，不带附件
        values = self.generate_message(
            res_id,
            [
                "subject",
                "body_html",
                "email_from",
                "message_email_to",
                "partner_to",
                "email_cc",
                "reply_to",
                "scheduled_date",
            ],
        )
        values["recipient_ids"] = [
            (4, pid) for pid in values.get("partner_ids", list())
        ]
        values["attachment_ids"] = [
            (4, aid) for aid in values.get("attachment_ids", list())
        ]
        values.update(email_values or {})
        attachment_ids = values.pop("attachment_ids", [])
        attachments = values.pop("attachments", [])
        # 添加防止无效的email_from的保护措施
        if "email_from" in values and not values.get("email_from"):
            values.pop("email_from")
        # 封装 body
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
                template_ctx = {
                    "message": self.env["mail.message"]
                    .sudo()
                    .new(
                        dict(body=values["body_html"], record_name=record.display_name)
                    ),
                    "model_description": self.env["ir.model"]
                    ._get(record._name)
                    .display_name,
                    "company": "company_id" in record
                    and record["company_id"]
                    or self.env.company,
                    "record": record,
                }
                body = template._render(
                    template_ctx, engine="ir.qweb", minimal_qcontext=True
                )
                values["body_html"] = self.env[
                    "mail.render.mixin"
                ]._replace_local_links(body)
        message = self.env["wxwork.mail"].sudo().create(values)

        # 管理附件
        for attachment in attachments:
            attachment_data = {
                "name": attachment[0],
                "datas": attachment[1],
                "type": "binary",
                "res_model": "mail.message",
                "res_id": message.mail_message_id.id,
            }
            attachment_ids.append((4, Attachment.create(attachment_data).id))
        if attachment_ids:
            message.write({"attachment_ids": attachment_ids})

        if force_send:
            # 强制发送
            message.send(raise_exception=raise_exception)
        return message.id  # TDE CLEANME: return mail + api.returns ?

    def copy_mail_template(self):
        """
        复制邮件模板为企业微信消息模板
        """
        for template in self.env["mail.template"].search([]):
            if self.name != template.name:
                self.create(
                    {
                        "name": template.name,
                        "model_id": template.model_id,
                        "model": template.model,
                        "subject": template.subject,
                        "email_from": template.email_from,
                        "use_default_to": template.use_default_to,
                        "message_email_to": template.message_email_to,
                        "partner_to": template.partner_to,
                        "email_cc": template.email_cc,
                        "reply_to": template.reply_to,
                        "body_html": Common(template.body_html).html2text_handle(),
                        "attachment_ids": template.attachment_ids,
                        "report_name": template.report_name,
                        "report_template": template.report_template,
                        "scheduled_date": template.scheduled_date,
                        "auto_delete": template.auto_delete,
                        "ref_ir_act_window": template.ref_ir_act_window,
                    }
                )


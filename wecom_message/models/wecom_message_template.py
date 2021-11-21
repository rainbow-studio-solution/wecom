# -*- coding: utf-8 -*-


import base64
import logging


from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class WeComMessageTemplate(models.Model):
    _name = "wecom.message.template"
    _inherit = ["mail.render.mixin"]
    _description = "Email Templates"
    _order = "name"

    # description
    name = fields.Char(string="Name", required=True, translate=True)
    subject = fields.Char(string="Subject", required=True)
    code = fields.Char(string="Code", required=True)
    model_id = fields.Many2one("ir.model", string="Applied to")
    model = fields.Char("Model", related="model_id.model")
    msgtype = fields.Selection(
        [
            ("text", "Text message"),
            ("image", "Picture message"),
            ("voice", "Voice messages"),
            ("video", "Video message"),
            ("file", "File message"),
            ("textcard", "Text card message"),
            ("news", "Graphic message"),
            ("mpnews", "Graphic message(mpnews)"),
            ("markdown", "Markdown message"),
            ("miniprogram", "Mini Program Notification Message"),
            ("taskcard", "Task card message"),
            ("template_card", "Template card message"),
        ],
        string="Message type",
        # required=True,
        default="text",
    )
    sender = fields.Char(
        "Sender",
    )

    # recipients
    message_to_user = fields.Char(string="To Users", help="Message recipients (users)")
    message_to_party = fields.Char(
        string="To Departments",
        help="Message recipients (departments)",
    )
    message_to_tag = fields.Char(
        string="To Tags",
        help="Message recipients (tags)",
    )

    # content
    media_id = fields.Many2one(
        string="Media file id",
        comodel_name="wecom.material",
        help="Media file ID, which can be obtained by calling the upload temporary material interface",
    )

    body_html = fields.Html("Html Body", translate=True, sanitize=False)
    body_not_html = fields.Text("Not Html Body", translate=True, default={})

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
        help="Indicates whether it is a confidential message, 0 indicates that it can be shared externally, 1 indicates that it cannot be shared and the content displays watermark, 2 indicates that it can only be shared within the enterprise, and the default is 0; Note that only messages of mpnews type support the safe value of 2, and other message types do not",
    )

    enable_id_trans = fields.Boolean(
        string="Turn on id translation",
        help="Indicates whether to enable ID translation, 0 indicates no, 1 indicates yes, and 0 is the default",
        default=False,
    )
    enable_duplicate_check = fields.Boolean(
        string="Turn on duplicate message checking",
        help="Indicates whether to enable duplicate message checking. 0 indicates no, 1 indicates yes. The default is 0",
        default=False,
    )
    duplicate_check_interval = fields.Integer(
        string="Time interval for repeated message checking",
        help="Indicates whether the message check is repeated. The default is 1800s and the maximum is no more than 4 hours",
        default="1800",
    )
    scheduled_date = fields.Char(
        "Scheduled Date",
        help="If set, the queue manager will send the email after the date. If not set, the email will be send as soon as possible. Jinja2 placeholders may be used.",
    )  # 如果设置，队列管理器将在日期后发送电子邮件。如果未设置，将尽快发送电子邮件。可以使用Jinja2占位符。
    auto_delete = fields.Boolean(
        "Auto Delete",
        default=True,
        help="This option permanently removes any track of messags after it's been sent, including from the Technical menu in the Settings, in order to preserve storage space of your Odoo database.",
    )  # 此选项将在发送电子邮件后永久删除任何电子邮件跟踪，包括从“设置”中的“技术”菜单中删除，以保留Odoo数据库的存储空间。

    _sql_constraints = [("code_uniq", "unique (code)", "Code must be unique !")]

    def get_template_by_code(self, code):
        record = self.search([("code", "=", code)])
        return record

    # ------------------------------------------------------------
    # 邮件/电子邮件值的生成
    # MESSAGE/EMAIL VALUES GENERATION
    # ------------------------------------------------------------
    def generate_recipients(self, results, res_ids):
        """
        生成模板的收件人。 如果模板或上下文要求，则可以生成默认值而不是模板值。
        如果上下文中有要求，可以将电子邮件（email_to，email_cc）转换为合作伙伴。
        """

        self.ensure_one()
        records = self.env[self.model].browse(res_ids).sudo()
        default_recipients = records._wecom_message_get_default_recipients()  # 默认接收者

        for res_id, recipients in default_recipients.items():
            results[res_id].update(recipients)
        print(str(default_recipients))
        if len(default_recipients) > 1:
            pass
        else:
            default_recipients = default_recipients[0]

        for res_id, recipients in default_recipients.items():
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
            # if self._context.get("tpl_partners_only"):
            #     # TODO 待处理 企业微信收件人
            mails = (
                tools.email_split(values.pop("message_to_all", ""))
                + tools.email_split(values.pop("message_to_user", ""))
                + tools.email_split(values.pop("message_to_party", ""))
                + tools.email_split(values.pop("message_to_tag", ""))
            )
            print("生成模板的收件人mails", mails)
            Partner = self.env["res.partner"]
            if records_company:
                Partner = Partner.with_context(
                    default_company_id=records_company[res_id]
                )
            for mail in mails:
                partner = Partner.find_or_create(mail)
                partner_ids.append(partner.id)

        print("生成模板的收件人results", results)
        return results

    def generate_message(self, res_ids, fields):
        """
        根据res_ids给定的记录，从给定给定模型的模板生成电子邮件。

        :param res_id: 用于呈现模板的记录的ID（模型来自模板定义）
        :returns: 包含所有用于创建新 mail.mail 条目的所有相关字段的字典，带有一个额外的键“附件”，格式为[（report_name，data）]，其中数据是base64编码的。
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
                if template.msgtype == "mpnews":
                    generated_field_values = template._render_field(
                        field,
                        template_res_ids,
                        post_process=(field == "body_html"),
                    )
                else:
                    generated_field_values = template._render_field(
                        field,
                        template_res_ids,
                        post_process=(field == "body_not_html"),
                    )

                for res_id, field_value in generated_field_values.items():
                    results.setdefault(res_id, dict())[field] = field_value
            # 计算收件人
            # if any(
            #     field in fields
            #     for field in [
            #         "message_to_all",
            #         "message_to_user",
            #         "message_to_party",
            #         "message_to_tag",
            #     ]
            # ):
            # print("--------------------")
            # print("计算收件人1", results, template_res_ids)
            # results = template.generate_recipients(results, template_res_ids)
            # print("--------------------")
            # print(
            #     "计算收件人2",
            #     results,
            # )
            # 更新所有res_id的值
            for res_id in template_res_ids:
                values = results[res_id]
                if values.get("body_html"):
                    values["body_html"] = tools.html_sanitize(values["body_html"])
                if values.get("body_not_html"):
                    # 删除html标记内的编码属性
                    values["body_not_html"] = tools.html_sanitize(
                        values["body_not_html"]
                    )
                # 技术设置
                values.update(
                    # mail_server_id=template.mail_server_id.id or False,
                    # auto_delete=template.auto_delete,
                    model=template.model,
                    res_id=res_id or False,
                    # attachment_ids=[attach.id for attach in template.attachment_ids],
                )

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
        message_values=None,
        notif_layout=False,
        company=None,
        use_templates=None,
        template_id=None,
    ):

        """
        生成一个新的mail.mail.  模板在由res_id和来自模板的模型给定的记录中呈现。

        :param int res_id: 呈现模板的记录的ID
        :param bool force_send: 立即强制发送邮件； 否则使用邮件队列（推荐）
        :param dict message_values: 使用这些值更新生成的消息，以进一步自定义消息；
        :param str notif_layout: 可选的通知布局，用于封装生成的邮件。企业微信消息仅用于mpnews消息格式，其他格式无效；
        :param bool is_wecom_message: True-通过企业微信发送消息；
        :returns: 创建的 mail.mail 的ID"""

        # is_wecom_message = self._context.get("is_wecom_message")

        # 仅在访问相关文档时才授予对 send_message 的访问权限
        self.ensure_one()
        self._send_check_access([res_id])

        # 根据值创建一个mail_mail，不带附件
        values = self.generate_message(
            res_id,
            [
                "subject",
                "msgtype",
                "sender",
                "message_to_all",
                "message_to_user",
                "message_to_party",
                "message_to_tag",
                "media_id",
                "body_html",
                "body_not_html",
                "safe",
                "enable_id_trans",
                "enable_duplicate_check",
                "duplicate_check_interval",
            ],
        )
        # values["recipient_ids"] = [
        #     (4, pid) for pid in values.get("partner_ids", list())
        # ]
        # values["attachment_ids"] = [
        #     (4, aid) for aid in values.get("attachment_ids", list())
        # ]
        values.update(message_values or {})
        # attachment_ids = values.pop("attachment_ids", [])
        # attachments = values.pop("attachments", [])

        # 添加防止无效的email_from的保护措施
        if "sender" in values and not values.get("sender"):
            values.pop("sender")
        # 封装 body_html
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
                    "message": self.env["wecom.message"]
                    .sudo()
                    .new(
                        dict(
                            body=values["body_html"],
                            record_name=record.display_name,
                        )
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

        # 封装 body_not_html
        if notif_layout and values["body_not_html"]:
            try:
                template = self.env.ref(notif_layout, raise_if_not_found=True)
            except ValueError:
                _logger.warning(
                    _(
                        "QWeb template %s not found when sending template %s. Sending without layouting."
                    )
                    % (notif_layout, self.name)
                )
            else:
                record = self.env[self.model].browse(res_id)
                template_ctx = {
                    "message": self.env["wecom.message"]
                    .sudo()
                    .new(
                        dict(
                            body=values["body_not_html"],
                            record_name=record.display_name,
                        )
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
                values["body_not_html"] = self.env[
                    "mail.render.mixin"
                ]._replace_local_links(body)

        if values.get("media_id"):
            values["media_id"] = self.media_id.id  # 指定对应的素材id

        values["use_templates"] = use_templates
        values["templates_id"] = template_id
        message = self.env["wecom.message"].sudo().create(values)

        if force_send:
            message.send(
                raise_exception=raise_exception,
                company=company,
            )
        return message.id  # TDE CLEANME: return mail + api.returns ?

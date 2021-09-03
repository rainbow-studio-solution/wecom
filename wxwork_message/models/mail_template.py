# -*- coding: utf-8 -*-

import base64
import logging

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class MailTemplate(models.Model):
    "Template for sending Enterprise WeChat message"

    _inherit = "mail.template"
    _description = "Enterprise WeChat Message Templates"
    _order = "name"

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
        required=True,
        default="text",
    )

    is_wxwork_message = fields.Boolean("Enterprise WeChat Message",)
    message_to_all = fields.Boolean("To all members",)
    message_to_user = fields.Char(string="To Users", help="Message recipients (users)",)
    message_to_party = fields.Char(
        string="To Departments", help="Message recipients (departments)",
    )
    message_to_tag = fields.Char(string="To Tags", help="Message recipients (tags)",)

    # content
    media_id = fields.Many2one(
        string="Media file id",
        comodel_name="wxwork.material",
        help="媒体文件Id,可以调用上传临时素材接口获取",
    )

    message_body_html = fields.Html("Html Body", translate=True, sanitize=False)
    message_body_json = fields.Text("Json Body", translate=True)

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

    # ------------------------------------------------------------
    # 邮件/电子邮件值的生成
    # MESSAGE/EMAIL VALUES GENERATION
    # ------------------------------------------------------------
    def generate_recipients(self, results, res_ids):
        """
        生成模板的收件人。 如果模板或上下文要求，则可以生成默认值而不是模板值。
        如果上下文中有要求，可以将电子邮件（email_to，email_cc）转换为合作伙伴。
        """
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
                # TODO 待处理 企业微信收件人
                mails = (
                    tools.email_split(values.pop("email_to", ""))
                    + tools.email_split(values.pop("email_cc", ""))
                    + tools.email_split(values.pop("message_to_user", ""))
                    + tools.email_split(values.pop("message_to_party", ""))
                    + tools.email_split(values.pop("message_to_tag", ""))
                )
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

        return super(MailTemplate, self).generate_recipients(results, res_ids)

    def generate_email(self, res_ids, fields):
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
                generated_field_values = template._render_field(
                    field, template_res_ids, post_process=(field == "body_html")
                )
                for res_id, field_value in generated_field_values.items():
                    results.setdefault(res_id, dict())[field] = field_value
            # 计算收件人
            if any(
                field in fields
                for field in [
                    "email_to",
                    "partner_to",
                    "email_cc",
                    "message_to_user",
                    "message_to_party",
                    "message_to_tag",
                ]
            ):
                results = template.generate_recipients(results, template_res_ids)
            # 更新所有res_id的值
            for res_id in template_res_ids:
                values = results[res_id]
                if values.get("body_html"):
                    values["body"] = tools.html_sanitize(values["body_html"])
                if values.get("message_body_html"):
                    # 删除html标记内的编码属性
                    values["message_body_html"] = tools.html_sanitize(
                        values["message_body_html"]
                    )
                # 技术设置
                values.update(
                    mail_server_id=template.mail_server_id.id or False,
                    auto_delete=template.auto_delete,
                    model=template.model,
                    res_id=res_id or False,
                    attachment_ids=[attach.id for attach in template.attachment_ids],
                )
            # 在附件中添加报告：为所有template_res_ids生成一次
            if template.report_template:
                for res_id in template_res_ids:
                    attachments = []
                    report_name = template._render_field("report_name", [res_id])[
                        res_id
                    ]
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

                    # TODO 在主干中，将返回格式更改为二进制以匹配message_post预期格式
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
    # EMAIL
    # ------------------------------------------------------------
    def send_mail(
        self,
        res_id,
        force_send=False,
        raise_exception=False,
        email_values=None,
        notif_layout=False,
        is_wxwork_message=None,
        company=None,
    ):
        """ 
        生成一个新的mail.mail.  模板在由res_id和来自模板的模型给定的记录中呈现。

        :param int res_id: 呈现模板的记录的ID
        :param bool force_send: 立即强制发送邮件； 否则使用邮件队列（推荐）
        :param dict email_values: 使用这些值更新生成的邮件，以进一步自定义邮件；
        :param str notif_layout: 可选的通知布局，用于封装生成的邮件。企业微信消息仅用于mpnews消息格式，其他格式无效； 
        :param bool is_wxwork_message: True-通过企业微信发送消息；
        :returns: 创建的 mail.mail 的ID  """
        # 仅在访问相关文档时才授予对 send_message 的访问权限
        self.ensure_one()
        self._send_check_access([res_id])

        Attachment = self.env[
            "ir.attachment"
        ]  # TDE FIXME: should remove default_type from context

        # 根据值创建一个mail_mail，不带附件
        values = self.generate_email(
            res_id,
            [
                "subject",
                "body_html",
                "email_from",
                "email_to",
                "partner_to",
                "email_cc",
                "reply_to",
                "scheduled_date",
                "msgtype",
                "message_to_all",
                "message_to_user",
                "message_to_party",
                "message_to_tag",
                "media_id",
                "message_body_html",
                "message_body_json",
                "safe",
                "enable_id_trans",
                "enable_duplicate_check",
                "duplicate_check_interval",
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
        if notif_layout and values["message_body_html"]:
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
                    "message": self.env["mail.message"]
                    .sudo()
                    .new(
                        dict(
                            body=values["message_body_html"],
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
                values["message_body_html"] = self.env[
                    "mail.render.mixin"
                ]._replace_local_links(body)

        if values.get("media_id"):
            values["media_id"] = self.media_id.id  # 指定对应的素材id

        if (
            "message_to_all" in values
            or "message_to_user" in values
            or "message_to_party" in values
            or "message_to_tag" in values
        ):
            if (
                values.get("message_to_all")
                or values.get("message_to_user")
                or values.get("message_to_party")
                or values.get("message_to_tag")
            ):
                values["is_wxwork_message"] = True  # 指定是企业微信消息

        mail = self.env["mail.mail"].sudo().create(values)

        # 管理附件
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
            mail.send(
                raise_exception=raise_exception,
                is_wxwork_message=is_wxwork_message,
                company=company,
            )
        return mail.id  # TDE CLEANME: return mail + api.returns ?

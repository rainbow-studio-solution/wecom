# -*- coding: utf-8 -*-

import ast
import base64
import re

from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError


def _reopen(self, res_id, model, context=None):
    # 在上下文中保存原始模型，因为选择可用模板列表需要上下文中的模型
    context = dict(context or {}, default_model=model)
    return {
        "type": "ir.actions.act_window",
        "view_mode": "form",
        "res_id": res_id,
        "res_model": self._name,
        "target": "new",
        "context": context,
    }


class MailComposer(models.TransientModel):
    """
    通用消息组合向导。您可以在模型和视图级别继承此向导以提供特定功能。

    向导的行为取决于“合成模式”字段：
    - 'comment':  记录在案。 该向导是通过``get_record_data`` 预先填充的
    - 'mass_mail': 批量邮件模式下的向导，其中邮件详细信息可以包含模板占位符，这些模板占位符将在发送给每个收件人之前与实际数据合并。
    """

    _inherit = "mail.compose.message"

    is_wecom_message = fields.Boolean(
        "WeCom Message",
    )
    message_to_user = fields.Char(
        string="To Employees",
        help="Message recipients (users)",
    )
    message_to_party = fields.Char(
        string="To Departments",
        help="Message recipients (departments)",
    )
    message_to_tag = fields.Char(
        string="To Tags",
        help="Message recipients (tags)",
    )

    media_id = fields.Many2one(
        string="Media file id",
        comodel_name="wecom.material",
        help="Media file ID, which can be obtained by calling the upload temporary material interface",
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
        default="text",
    )
    body_html = fields.Html("Html Contents", default="", sanitize_style=True)
    body_json = fields.Text("Json Contents", default="", sanitize_style=True)
    body_markdown = fields.Text("Markdown Contents", default="", sanitize_style=True)
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

    # ------------------------------------------------------------
    # 动作
    # ACTIONS
    # ------------------------------------------------------------

    def send_mail(self, auto_commit=False):
        """
        处理向导的内容，然后继续发送相关的电子邮件，并在需要时动态呈现任何模板模式。
        """
        is_wecom_message = self._context.get("is_wecom_message")
        notif_layout = self._context.get("custom_layout")
        # 几种自定义布局在渲染时会使用模型描述，例如 在“查看<document>”按钮中。 某些模型用于不同的业务概念，例如用于RFQ和PO的'purchase.order'。 为避免混淆，我们必须根据对象的状态使用不同的措词。
        # 因此，我们可以从一开始就在上下文中设置描述，以避免退回到在'_notify_prepare_template_context'中检索到的常规display_name上。
        model_description = self._context.get("model_description")
        for wizard in self:
            # 链接到email.template的重复附件。
            # 确实，基本的mail.compose.message向导以群发邮件模式复制附件。 但是在“单一帖子”模式下，还必须复制电子邮件模板的附件，以避免更改其所有权。
            if (
                wizard.attachment_ids
                and wizard.composition_mode != "mass_mail"
                and wizard.template_id
            ):
                new_attachment_ids = []
                for attachment in wizard.attachment_ids:
                    if attachment in wizard.template_id.attachment_ids:
                        new_attachment_ids.append(
                            attachment.copy(
                                {
                                    "res_model": "mail.compose.message",
                                    "res_id": wizard.id,
                                }
                            ).id
                        )
                    else:
                        new_attachment_ids.append(attachment.id)
                new_attachment_ids.reverse()
                wizard.write({"attachment_ids": [(6, 0, new_attachment_ids)]})

            # 指定是企业微信消息
            if is_wecom_message:
                wizard.is_wecom_message = True

            # 群发邮件
            mass_mode = wizard.composition_mode in ("mass_mail", "mass_post")

            ActiveModel = (
                self.env[wizard.model]
                if wizard.model and hasattr(self.env[wizard.model], "message_post")
                else self.env["mail.thread"]
            )
            if wizard.composition_mode == "mass_post":
                # 不要直接发送电子邮件，而是使用队列来添加上下文密钥，以避免订阅作者
                ActiveModel = ActiveModel.with_context(
                    mail_notify_force_send=False, mail_create_nosubscribe=True
                )
            # 向导以批处理模式工作：[res_id]或active_ids或active_domain
            if mass_mode and wizard.use_active_domain and wizard.model:
                res_ids = (
                    self.env[wizard.model]
                    .search(ast.literal_eval(wizard.active_domain))
                    .ids
                )
            elif mass_mode and wizard.model and self._context.get("active_ids"):
                res_ids = self._context["active_ids"]
            else:
                res_ids = [wizard.res_id]

            batch_size = (
                int(self.env["ir.config_parameter"].sudo().get_param("mail.batch_size"))
                or self._batch_size
            )
            sliced_res_ids = [
                res_ids[i : i + batch_size] for i in range(0, len(res_ids), batch_size)
            ]

            if (
                wizard.composition_mode == "mass_mail"
                or wizard.is_log
                or (wizard.composition_mode == "mass_post" and not wizard.notify)
            ):  # 日志记录：子类型为False
                subtype_id = False
            elif wizard.subtype_id:
                subtype_id = wizard.subtype_id.id
            else:
                subtype_id = self.env["ir.model.data"].xmlid_to_res_id(
                    "mail.mt_comment"
                )

            for res_ids in sliced_res_ids:
                # 批量邮件模式：邮件被伪装，因为通过get_mail_values进行浏览时，将检查相关记录的标准访问权限以计算邮件值。 如果人们可以访问记录，则他们有权使用sudo创建大量电子邮件，因为这被认为是一种技术模型。

                batch_mails_sudo = self.env["mail.mail"].sudo()
                all_mail_values = wizard.get_mail_values(
                    res_ids
                )  # 生成send_mail用来创建mail_messages或mail_mails的值。
                for res_id, mail_values in all_mail_values.items():
                    if wizard.composition_mode == "mass_mail":
                        batch_mails_sudo |= (
                            self.env["mail.mail"].sudo().create(mail_values)
                        )
                    else:
                        post_params = dict(
                            message_type=wizard.message_type,
                            is_wecom_message=wizard.is_wecom_message,
                            subtype_id=subtype_id,
                            email_layout_xmlid=notif_layout,
                            add_sign=not bool(wizard.template_id),
                            mail_auto_delete=wizard.template_id.auto_delete
                            if wizard.template_id
                            else False,
                            model_description=model_description,
                        )
                        post_params.update(mail_values)

                        if ActiveModel._name == "mail.thread":
                            if wizard.model:
                                post_params["model"] = wizard.model
                                post_params["res_id"] = res_id
                            if not ActiveModel.message_notify(**post_params):
                                # 如果message_notify返回空记录集，则找不到收件人。
                                raise UserError(_("No recipient found."))
                        else:
                            ActiveModel.browse(res_id).message_post(**post_params)

                if wizard.composition_mode == "mass_mail":
                    # 群发模式
                    batch_mails_sudo.send(
                        auto_commit=auto_commit, is_wecom_message=is_wecom_message
                    )

    def get_mail_values(self, res_ids):
        """
        生成send_mail用来创建mail_messages或mail_mails的值。
        """
        self.ensure_one()
        results = dict.fromkeys(res_ids, False)
        rendered_values = {}
        mass_mail_mode = self.composition_mode == "mass_mail"

        # 一次呈现所有基于模板的值
        if mass_mail_mode and self.model:
            rendered_values = self.render_message(res_ids)
        # 批量计算基于别名的回复
        reply_to_value = dict.fromkeys(res_ids, None)
        if mass_mail_mode and not self.no_auto_thread:
            records = self.env[self.model].browse(res_ids)
            reply_to_value = records._notify_get_reply_to(default=self.email_from)

        blacklisted_rec_ids = set()
        if mass_mail_mode and issubclass(
            type(self.env[self.model]), self.pool["mail.thread.blacklist"]
        ):
            self.env["mail.blacklist"].flush(["email"])
            self._cr.execute("SELECT email FROM mail_blacklist")
            blacklist = {x[0] for x in self._cr.fetchall()}
            if blacklist:
                targets = (
                    self.env[self.model].browse(res_ids).read(["email_normalized"])
                )
                # 首先从收件人中提取电子邮件，然后再与黑名单进行比较
                blacklisted_rec_ids.update(
                    target["id"]
                    for target in targets
                    if target["email_normalized"] in blacklist
                )

        for res_id in res_ids:
            # 静态向导（mail.message）值
            mail_values = {
                "subject": self.subject,
                "body": self.body or "",
                "parent_id": self.parent_id and self.parent_id.id,
                "partner_ids": [partner.id for partner in self.partner_ids],
                "attachment_ids": [attach.id for attach in self.attachment_ids],
                "author_id": self.author_id.id,
                "email_from": self.email_from,
                "record_name": self.record_name,
                "no_auto_thread": self.no_auto_thread,
                "mail_server_id": self.mail_server_id.id,
                "mail_activity_type_id": self.mail_activity_type_id.id,
                "is_wecom_message": self.is_wecom_message,
                "msgtype": self.msgtype,
                "media_id": self.media_id.id,
                "message_to_user": self.message_to_user,
                "message_to_party": self.message_to_party,
                "message_to_tag": self.message_to_tag,
                "body_html": self.body_html,
                "body_json": self.body_json,
                "safe": self.safe,
                "enable_id_trans": self.enable_id_trans,
                "enable_duplicate_check": self.enable_duplicate_check,
                "duplicate_check_interval": self.duplicate_check_interval,
            }

            # 指定通知方式
            # if self.is_wecom_message:
            #     mail_values.update(notification_type="wxwork")

            # 群发邮件：呈现替代向导的静态值
            if mass_mail_mode and self.model:
                record = self.env[self.model].browse(res_id)
                mail_values["headers"] = record._notify_email_headers()
                # keep a copy unless specifically requested, reset record name (avoid browsing records)
                mail_values.update(
                    notification=not self.auto_delete_message,
                    model=self.model,
                    res_id=res_id,
                    record_name=False,
                )
                # 自动删除mail_mail
                if self.auto_delete or self.template_id.auto_delete:
                    mail_values["auto_delete"] = True
                # 使用模板渲染
                email_dict = rendered_values[res_id]
                mail_values["partner_ids"] += email_dict.pop("partner_ids", [])
                mail_values.update(email_dict)
                if not self.no_auto_thread:
                    mail_values.pop("reply_to")
                    if reply_to_value.get(res_id):
                        mail_values["reply_to"] = reply_to_value[res_id]
                if self.no_auto_thread and not mail_values.get("reply_to"):
                    mail_values["reply_to"] = mail_values["email_from"]
                # mail_mail values: body -> body_html, partner_ids -> recipient_ids
                mail_values["body_html"] = mail_values.get("body", "")
                mail_values["body_html"] = mail_values.get("body_html", "")
                mail_values["body_json"] = mail_values.get("body_json", "")
                mail_values["recipient_ids"] = [
                    (4, id) for id in mail_values.pop("partner_ids", [])
                ]

                # 流程附件：在由message_post / mail_mail创建之前，不应进行编码
                mail_values["attachments"] = [
                    (name, base64.b64decode(enc_cont))
                    for name, enc_cont in email_dict.pop("attachments", list())
                ]
                attachment_ids = []
                for attach_id in mail_values.pop("attachment_ids"):
                    new_attach_id = (
                        self.env["ir.attachment"]
                        .browse(attach_id)
                        .copy({"res_model": self._name, "res_id": self.id})
                    )
                    attachment_ids.append(new_attach_id.id)
                attachment_ids.reverse()
                mail_values["attachment_ids"] = self.env[
                    "mail.thread"
                ]._message_post_process_attachments(
                    mail_values.pop("attachments", []),
                    attachment_ids,
                    {"model": "mail.message", "res_id": 0},
                )[
                    "attachment_ids"
                ]
                # 通过将邮件状态设置为取消来过滤出列入黑名单的记录->用于群发邮件统计信息
                if res_id in blacklisted_rec_ids:
                    mail_values["state"] = "cancel"
                    # 不要将邮件发布到收件人的聊天记录中
                    mail_values["notification"] = False

            results[res_id] = mail_values
        return results

    # ------------------------------------------------------------
    # 模板
    # TEMPLATES
    # ------------------------------------------------------------

    def onchange_template_id(self, template_id, composition_mode, model, res_id):
        """
        - mass_mailing: 我们无法渲染，因此返回模板值
        - normal mode: 返回渲染值
        /!\ 对于x2many字段，此onchange返回命令而不是id
        """
        if template_id and composition_mode == "mass_mail":
            # template_info = template_id
            # 邮件模板
            template = self.env["mail.template"].browse(template_id)
            fields = [
                "subject",
                "media_id",
                "body_html",
                "email_from",
                "reply_to",
                "mail_server_id",
                "message_to_user",
                "message_to_party",
                "message_to_tag",
                "msgtype",
                "body_html",
                "body_json",
                "safe",
                "enable_id_trans",
                "enable_duplicate_check",
                "duplicate_check_interval",
            ]
            values = dict(
                (field, getattr(template, field))
                for field in fields
                if getattr(template, field)
            )

            if template.attachment_ids:
                values["attachment_ids"] = [att.id for att in template.attachment_ids]

            if template.mail_server_id:
                values["mail_server_id"] = template.mail_server_id.id

        elif template_id:
            values = self.generate_email_for_composer(
                template_id,
                [res_id],
                [
                    "subject",
                    "body_html",
                    "email_from",
                    "email_to",
                    "partner_to",
                    "email_cc",
                    "reply_to",
                    "attachment_ids",
                    "mail_server_id",
                    "msgtype",
                    "media_id",
                    "message_to_user",
                    "message_to_party",
                    "message_to_tag",
                    "body_html",
                    "body_json",
                    "safe",
                    "enable_id_trans",
                    "enable_duplicate_check",
                    "duplicate_check_interval",
                ],
            )[res_id]

            # 将附件转换为attachment_ids； 未附加到文档，因为这将在发布过程中进一步完成，如果未发送电子邮件，则允许清除数据库
            attachment_ids = []
            Attachment = self.env["ir.attachment"]
            for attach_fname, attach_datas in values.pop("attachments", []):
                data_attach = {
                    "name": attach_fname,
                    "datas": attach_datas,
                    "res_model": "mail.compose.message",
                    "res_id": 0,
                    "type": "binary",  # 从上下文覆盖default_type，可能意味着要使用另一个模型！
                }
                attachment_ids.append(Attachment.create(data_attach).id)
            if values.get("attachment_ids", []) or attachment_ids:
                values["attachment_ids"] = [
                    (6, 0, values.get("attachment_ids", []) + attachment_ids)
                ]
        else:
            default_values = self.with_context(
                default_composition_mode=composition_mode,
                default_model=model,
                default_res_id=res_id,
            ).default_get(
                [
                    "composition_mode",
                    "model",
                    "res_id",
                    "parent_id",
                    "partner_ids",
                    "subject",
                    "body",
                    "email_from",
                    "reply_to",
                    "attachment_ids",
                    "mail_server_id",
                    "msgtype",
                    "media_id",
                    "message_to_user",
                    "message_to_party",
                    "message_to_tag",
                    "body_html",
                    "body_json",
                    "safe",
                    "enable_id_trans",
                    "enable_duplicate_check",
                    "duplicate_check_interval",
                ]
            )
            values = dict(
                (key, default_values[key])
                for key in [
                    "subject",
                    "body",
                    "partner_ids",
                    "email_from",
                    "reply_to",
                    "attachment_ids",
                    "mail_server_id",
                    "msgtype",
                    "media_id",
                    "message_to_user",
                    "message_to_party",
                    "message_to_tag",
                    "body_html",
                    "body_json",
                    "safe",
                    "enable_id_trans",
                    "enable_duplicate_check",
                    "duplicate_check_interval",
                ]
                if key in default_values
            )

        if values.get("body_html"):
            values["body"] = values.pop("body_html")
        if values.get("body_html"):
            values["body_html"] = values.pop("body_html")
        if values.get("body_json"):
            values["body_json"] = values.pop("body_json")

        # 此onchange应该返回命令，而不是x2many字段的ID。
        values = self._convert_to_write(values)

        return {"value": values}

    def save_as_template(self):
        """
        点击“另存为模板”按钮：当前表单值将是附加到当前文档的新模板。
        """
        for record in self:
            model = self.env["ir.model"]._get(record.model or "mail.message")
            model_name = model.name or ""
            template_name = "%s: %s" % (model_name, tools.ustr(record.subject))
            values = {
                "name": template_name,
                "subject": record.subject or False,
                "body_html": record.body or False,
                "model_id": model.id or False,
                "attachment_ids": [(6, 0, [att.id for att in record.attachment_ids])],
                "msgtype": record.msgtype or False,
                "message_to_user": record.message_to_user or False,
                "message_to_party": record.message_to_party or False,
                "message_to_tag": record.message_to_tag or False,
                "media_id": record.media_id or False,
                "body_html": record.body_html or False,
                "body_json": record.body_json or False,
                "safe": record.safe or False,
                "enable_id_trans": record.enable_id_trans or False,
                "enable_duplicate_check": record.enable_duplicate_check or False,
                "duplicate_check_interval": record.duplicate_check_interval or False,
            }
            template = self.env["mail.template"].create(values)
            # generate the saved template
            record.write({"template_id": template.id})
            record.onchange_template_id_wrapper()

            return _reopen(self, record.id, record.model, context=self._context)

    # ------------------------------------------------------------
    # 渲染
    # RENDERING
    # ------------------------------------------------------------

    def render_message(self, res_ids):
        """
        为res_ids给定的文档记录生成基于模板的向导值。 此方法将由email_template继承，使用Jinja2模板将生成更完整的字典。

        将为所有res_ids生成每个模板，从而允许对模板进行一次解析，然后多次渲染。 这对于批量邮件非常有用，在这种情况下，模板呈现是流程的重要组成部分。

        还根据mail_thread方法_message_get_default_recipients计算默认收件人。 这可以确保总有问题的总是指定一些接收者。

        :param browse wizard: 当前的mail.compose.message浏览记录
        :param list res_ids: list of record ids

        :return dict results: 对于每个res_id，生成的主题，正文，email_from和reply_to模板值
        """
        self.ensure_one()
        multi_mode = True
        if isinstance(res_ids, int):
            multi_mode = False
            res_ids = [res_ids]

        subjects = self.env["mail.render.mixin"]._render_template(
            self.subject, self.model, res_ids
        )
        bodies = self.env["mail.render.mixin"]._render_template(
            self.body, self.model, res_ids, post_process=True
        )
        bodies_html = self.env["mail.render.mixin"]._render_template(
            self.body_html, self.model, res_ids, post_process=True
        )
        bodies_text = self.env["mail.render.mixin"]._render_template(
            self.body_json, self.model, res_ids, post_process=True
        )
        emails_from = self.env["mail.render.mixin"]._render_template(
            self.email_from, self.model, res_ids
        )
        replies_to = self.env["mail.render.mixin"]._render_template(
            self.reply_to, self.model, res_ids
        )
        message_to_user = self.env["mail.render.mixin"]._render_template(
            self.message_to_user, self.model, res_ids
        )
        message_to_party = self.env["mail.render.mixin"]._render_template(
            self.message_to_party, self.model, res_ids
        )
        message_to_tag = self.env["mail.render.mixin"]._render_template(
            self.message_to_tag, self.model, res_ids
        )
        # ！！！重点标识！！！ 处理收件人
        default_recipients = {}
        if not self.partner_ids:
            records = self.env[self.model].browse(res_ids).sudo()
            default_recipients = records._message_get_default_recipients()

        results = dict.fromkeys(res_ids, False)
        for res_id in res_ids:
            results[res_id] = {
                "subject": subjects[res_id],
                "body": bodies[res_id],
                "body_html": bodies_html[res_id],
                "body_json": bodies_text[res_id],
                "email_from": emails_from[res_id],
                "reply_to": replies_to[res_id],
                "message_to_user": message_to_user[res_id],
                "message_to_party": message_to_party[res_id],
                "message_to_tag": message_to_tag[res_id],
            }
            results[res_id].update(default_recipients.get(res_id, dict()))

        # 生成基于模板的值
        if self.template_id:
            template_values = self.generate_email_for_composer(
                self.template_id.id,
                res_ids,
                [
                    "email_to",
                    "partner_to",
                    "email_cc",
                    "attachment_ids",
                    "mail_server_id",
                    "message_to_user",
                    "message_to_party",
                    "message_to_tag",
                ],
            )
        else:
            template_values = {}

        for res_id in res_ids:
            if template_values.get(res_id):
                # 收件人由模板管理
                results[res_id].pop("partner_ids", None)
                results[res_id].pop("email_to", None)
                results[res_id].pop("email_cc", None)
                # results[res_id].pop("message_to_user", None)
                # results[res_id].pop("message_to_party", None)
                # results[res_id].pop("message_to_tag", None)
                # 从模板值中删除附件，因为它们不应呈现
                template_values[res_id].pop("attachment_ids", None)
            else:
                template_values[res_id] = dict()
            # 通过composer值更新模板值
            template_values[res_id].update(results[res_id])

        return multi_mode and template_values or template_values[res_ids[0]]

    @api.model
    def generate_email_for_composer(self, template_id, res_ids, fields):
        """
        调用 email_template.generate_email()，获取与mail.compose.message相关的字段，将email_cc和email_to转换为partner_ids
        """
        multi_mode = True
        if isinstance(res_ids, int):
            multi_mode = False
            res_ids = [res_ids]

        returned_fields = fields + ["partner_ids", "attachments"]
        values = dict.fromkeys(res_ids, False)

        template_values = (
            self.env["mail.template"]
            .with_context(tpl_partners_only=True)
            .browse(template_id)
            .generate_email(res_ids, fields)
        )

        for res_id in res_ids:
            res_id_values = dict(
                (field, template_values[res_id][field])
                for field in returned_fields
                if template_values[res_id].get(field)
            )

            res_id_values["body"] = res_id_values.pop("body_html", "")
            res_id_values["body_html"] = res_id_values.pop("body_html", "")
            res_id_values["body_json"] = res_id_values.pop("body_json", "")
            values[res_id] = res_id_values

        return multi_mode and values or values[res_ids[0]]

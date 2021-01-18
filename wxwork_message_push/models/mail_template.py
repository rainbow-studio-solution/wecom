# -*- coding: utf-8 -*-

import base64
import logging
from ...wxwork_api.wx_qy_api.CorpApi import *


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
    wxwork_body_html = fields.Text("Enterprise WeChat Message Body", sanitize=False)
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
    def create_wxwork_wxwork_template(self, vals_list):
        return super().create(vals_list)

    @api.model
    def copy_body_html(self):
        """
        复制邮件模板为企业微信消息模板
        """
        for template in self.search([]):
            if not template.wxwork_body_html:
                # 判断企业微信消息模板为空
                template.wxwork_body_html = self.html2text_handle(template.body_html)
            else:
                template.wxwork_body_html = None

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
            # 根据值创建一个消息，不带附件
            values = self.generate_wxwork_message(
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

            params = self.env["ir.config_parameter"].sudo()
            corpid = params.get_param("wxwork.corpid")
            secret = params.get_param("wxwork.message_secret")
            message_agentid = params.get_param("wxwork.message_agentid")
            debug = params.get_param("wxwork.debug_enabled")
            wxapi = CorpApi(corpid, secret)
            try:
                response = wxapi.httpCall(
                    CORP_API_TYPE["MESSAGE_SEND"],
                    {
                        "touser": values["email_to"],
                        "msgtype": "markdown",
                        "agentid": int(message_agentid),
                        "markdown": {
                            "content": "%s %s "
                            % (
                                "# " + values["subject"] + "\n",
                                values["wxwork_body_html"],
                            )
                        },
                        "enable_duplicate_check": 0,
                        "duplicate_check_interval": 1800,
                    },
                )
                # TODO 待处理发送失败的信息
            except ApiException as e:
                if debug:
                    print(
                        _(
                            "发送错误, error: %s",
                            (str(e.errCode), Errcode.getErrcode(e.errCode), e.errMsg),
                        )
                    )
        else:
            # Grant access to send_mail only if access to related document
            self.ensure_one()
            self._send_check_access([res_id])

            Attachment = self.env[
                "ir.attachment"
            ]  # TDE FIXME: should remove default_type from context

            # create a mail_mail based on values, without attachments
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
            # add a protection against void email_from
            if "email_from" in values and not values.get("email_from"):
                values.pop("email_from")
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
                    template_ctx = {
                        "message": self.env["mail.message"]
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
            mail = self.env["mail.mail"].sudo().create(values)

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

    def generate_wxwork_message(self, res_ids, fields):

        """
        基于由res_ids提供的记录，从给定给定模型的模板生成 企业微信消息。

        :param res_id: 用于呈现模板的记录的ID（模型来自模板定义）
        :returns: 包含所有用于创建新mail.mail条目的所有相关字段的字典，带有一个额外的键 ``附件``，格式为[(report_name, data)]，其中数据是base64编码的。
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
                generated_field_values = template._render_wxwork_message_field(
                    field, template_res_ids, post_process=(field == "wxwork_body_html")
                )

                for res_id, field_value in generated_field_values.items():
                    results.setdefault(res_id, dict())[field] = field_value

            # 计算收件人
            if any(field in fields for field in ["email_to", "partner_to", "email_cc"]):
                results = template.generate_wxwork_message_recipients(
                    results, template_res_ids
                )

            # 更新所有res_id的值
            for res_id in template_res_ids:
                values = results[res_id]
                if values.get("wxwork_body_html"):
                    values["body"] = tools.html_sanitize(values["wxwork_body_html"])
                # if values.get("body_html"):
                #     values["body"] = tools.html_sanitize(values["body_html"])

                # 技术设置
                values.update(
                    mail_server_id=template.mail_server_id.id or False,
                    auto_delete=template.auto_delete,
                    model=template.model,
                    res_id=res_id or False,
                    attachment_ids=[attach.id for attach in template.attachment_ids],
                )

        return multi_mode and results or results[res_ids[0]]

    def generate_wxwork_message_recipients(self, results, res_ids):
        """
        生成模板的收件人。 如果模板或上下文要求，则可以生成默认值而不是模板值。
        如果上下文中有要求，可以将电子邮件（email_to，email_cc）转换为合作伙伴
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
                messages = tools.email_split(
                    values.pop("email_to", "")
                ) + tools.email_split(values.pop("email_cc", ""))
                Partner = self.env["res.partner"]
                if records_company:
                    Partner = Partner.with_context(
                        default_company_id=records_company[res_id]
                    )
                for message in messages:
                    partner = Partner.find_or_create(message)
                    partner_ids.append(partner.id)
            partner_to = values.pop("partner_to", "")
            if partner_to:
                # placeholders could generate '', 3, 2 due to some empty field values
                tpl_partner_ids = [int(pid) for pid in partner_to.split(",") if pid]
                partner_ids += (
                    self.env["res.partner"].sudo().browse(tpl_partner_ids).exists().ids
                )
            # TODO 获取企业微信用户id
            results[res_id]["email_to"] = (
                self.env["res.users"].sudo().browse(res_ids).wxwork_id
            )
            results[res_id]["partner_ids"] = partner_ids

        return results

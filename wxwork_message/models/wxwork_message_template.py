# -*- coding: utf-8 -*-

import base64
import logging

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class WxWorkMessageTemplate(models.Model):
    "Template for sending Enterprise WeChat message"
    _name = "wxwork.message.template"
    _inherit = ["mail.render.mixin"]
    _description = "Enterprise WeChat Message Templates"
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
    subject = fields.Char(
        "Subject", translate=True, help="Subject (placeholders may be used here)"
    )
    model_id = fields.Many2one(
        "ir.model",
        string="Applies to",
        required=True,
        domain=["&", ("is_mail_thread_wxwork", "=", True), ("transient", "=", False)],
        help="可以与该模板一起使用的文档类型",
        ondelete="cascade",
    )
    model = fields.Char(
        "Related Document Model", related="model_id.model", index=True, store=True,
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
            ("mpnews", "Graphic message(mpnews)"),
            ("markdown", "Markdown message"),
            ("miniprogram", "Mini Program Notification Message"),
            ("taskcard", "Task card message"),
        ],
        string="Message type",
        required=True,
        default="text",
    )

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
    body_text = fields.Text("Body", translate=True,)
    body_html = fields.Html("Body", translate=True, sanitize=False)
    # 用于创建上下文操作（与电子邮件模板相同）
    sidebar_action_id = fields.Many2one(
        "ir.actions.act_window",
        "Sidebar action",
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
    scheduled_date = fields.Char(
        "Scheduled Date",
        help="If set, the queue manager will send the email after the date. If not set, the email will be send as soon as possible. Jinja2 placeholders may be used.",
    )
    auto_delete = fields.Boolean(
        "Auto Delete",
        default=True,
        help="This option permanently removes any track of email after it's been sent, including from the Technical menu in the Settings, in order to preserve storage space of your Odoo database.",
    )
    # contextual action
    ref_ir_act_window = fields.Many2one(
        "ir.actions.act_window",
        "Sidebar action",
        readonly=True,
        copy=False,
        help="Sidebar action to make this template available on records "
        "of the related document model",
    )

    def unlink(self):
        self.sudo().mapped("sidebar_action_id").unlink()
        return super(WxWorkMessageTemplate, self).unlink()

    @api.returns("self", lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {}, name=_("%s (copy)", self.name))
        return super(WxWorkMessageTemplate, self).copy(default=default)

    def unlink_action(self):
        for template in self:
            if template.ref_ir_act_window:
                template.ref_ir_act_window.unlink()
        return True

    def action_create_sidebar_action(self):
        ActWindow = self.env["ir.actions.act_window"]
        view = self.env.ref("sms.sms_composer_view_form")

        for template in self:
            button_name = _("Send Message (%s)", template.name)
            action = ActWindow.create(
                {
                    "name": button_name,
                    "type": "ir.actions.act_window",
                    "res_model": "wxwork.message.composer",
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
        如果上下文中有要求，可以将消息（message_to_user，）转换为合作伙伴。 
        """
        self.ensure_one()

        # if self.use_default_to or self._context.get("tpl_force_default_to"):
        #     records = self.env[self.model].browse(res_ids).sudo()
        #     default_recipients = records._message_get_default_recipients()
        #     for res_id, recipients in default_recipients.items():
        #         results[res_id].pop("partner_to", None)
        #         results[res_id].update(recipients)

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
                    values.pop("message_to_user", "")
                ) + tools.email_split(values.pop("message_to_party", ""))
                Partner = self.env["res.partner"]
                if records_company:
                    Partner = Partner.with_context(
                        default_company_id=records_company[res_id]
                    )
                for message in messages:
                    partner = Partner.find_or_create(message)
                    partner_ids.append(partner.id)
            # partner_to = values.pop("partner_to", "")
            # if partner_to:
            #     # placeholders could generate '', 3, 2 due to some empty field values
            #     tpl_partner_ids = [int(pid) for pid in partner_to.split(",") if pid]
            #     partner_ids += (
            #         self.env["res.partner"].sudo().browse(tpl_partner_ids).exists().ids
            #     )
            # results[res_id]["partner_ids"] = partner_ids
        return results

    def generate_message(self, res_ids, fields):
        """
        根据res_ids给定的记录，从给定给定模型的模板生成消息。 

        :param res_id: 用于呈现模板的记录的ID（模型来自模板定义） 
        :returns: 包含所有用于创建新wxwork.message条目的所有相关字段的字典。
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
            # print("template", template)
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
                for field in ["message_to_user", "message_to_party", "message_to_tag"]
            ):
                results = template.generate_recipients(results, template_res_ids)

            # 更新所有res_id的值
            for res_id in template_res_ids:
                values = results[res_id]
                if values.get("body_html"):
                    values["body_html"] = tools.html_sanitize(values["body_html"])

                # 技术设置
                values.update(
                    auto_delete=template.auto_delete,
                    model=template.model,
                    res_id=res_id or False,
                )

        return multi_mode and results or results[res_ids[0]]

    # ------------------------------------------------------------
    # 企业微信消息
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
    ):
        """ 
        生成一个新的wxwork.message， 模板在由res_id和来自模板的模型给定的记录中呈现。 

        :param int res_id: 呈现模板的记录的ID 
        :param bool force_send: 立即强制发送消息； 否则使用消息队列（推荐）
        :param dict message_values: 使用这些值更新生成的消息，以进一步自定义消息；
        :param str notif_layout: 可选的通知布局，用于封装生成的消息,仅用于mpnews消息格式，其他格式无效； 
        :returns: 创建的wxwork.message的ID 
        """

        # 仅在访问相关文档时才授予对 send_message 的访问权限
        self.ensure_one()
        self._send_check_access([res_id])

        values = self.generate_message(
            res_id,
            [
                "subject",
                "msgtype",
                "message_to_all",
                "message_to_user",
                "message_to_party",
                "message_to_tag",
                "body_html",
                "body_text",
                "safe",
                "enable_id_trans",
                "enable_duplicate_check",
                "duplicate_check_interval",
                "scheduled_date",
            ],
        )
        values["notification_type"] = "wxwork"  # 指定通知方式
        values["message_type"] = "wxwork"  # 指定邮件消息类型
        values.update(message_values or {})
        print("values", values)
        # 封装消息内容
        if values["msgtype"] == "mpnews":
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
        else:
            pass

        mail = self.env["mail.mail"].sudo().create(values)
        # print("message", message)

        if force_send:
            mail.send_wxwork_message(raise_exception=raise_exception)
        return mail.id  # TDE CLEANME: return mail + api.returns ?

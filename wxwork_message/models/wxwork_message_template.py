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
        default="markdown",
    )

    email_to_all = fields.Boolean("To all members",)
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


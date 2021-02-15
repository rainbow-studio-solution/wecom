# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ServerActions(models.Model):
    """ 
    在服务器操作中添加 企业微信消息 选项
    """

    _name = "ir.actions.server"
    _inherit = ["ir.actions.server"]

    state = fields.Selection(
        selection_add=[("wxwork", "Send Enterprise WeChat Message"),],
        ondelete={"wxwork": "cascade"},
    )

    wxwork_message_template_id = fields.Many2one(
        "wxwork.message.template",
        "Enterprise WeChat Message Template",
        ondelete="set null",
        domain="[('model_id', '=', model_id)]",
    )

    wxwork_message_mass_keep_log = fields.Boolean(
        "Log as Note", default=True, help="记录为备注 "
    )

    @api.constrains("state", "model_id")
    def _check_wxwork_message_capability(self):
        for action in self:
            if action.state == "wxwork" and not action.model_id.is_mail_thread:
                # 发送企业微信消息 只能在mail.thread模型上完成
                raise ValidationError(
                    _(
                        "Sending Enterprise WeChat Message can only be done on a mail.thread model"
                    )
                )

    def _run_action_wxwork_message_multi(self, eval_context=None):
        # TDE CLEANME: 使用服务器操作转到新的api时，删除操作
        if not self.wxwork_message_template_id or self._is_recompute():
            return False

        records = eval_context.get("records") or eval_context.get("record")
        if not records:
            return False

        composer = (
            self.env["wxwork.message.composer"]
            .with_context(
                default_res_model=records._name,
                default_res_ids=records.ids,
                default_composition_mode="mass",
                default_template_id=self.wxwork_message_template_id.id,
                default_mass_keep_log=self.wxwork_message_mass_keep_log,
            )
            .create({})
        )
        composer.action_send_sms()
        return False

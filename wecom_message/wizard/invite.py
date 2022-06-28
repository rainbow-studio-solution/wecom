# -*- coding: utf-8 -*-

from lxml import etree
from lxml.html import builder as html

from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError


class Invite(models.TransientModel):
    _inherit = "mail.wizard.invite"

    send_mail = fields.Boolean(
        "Send Email",
        default=False,
        help="If checked, the partners will receive an email warning they have been added in the document's followers.",
    )
    send_wecom_message = fields.Boolean(
        "Send Wecom Message",
        default=True,
        help="If checked, the partners will receive an message warning they have been added in the document's followers.",
    )

    def _check_is_wecom_message(self, message_values):
        """
        判断是否是企微消息
        """
        model = message_values["model"]
        res_id = message_values["res_id"]
        fields = self.env[model]._fields.keys()
        if "is_wecom_user" in fields:
            return self.env[model].browse(res_id).is_wecom_user
        else:
            return False

    def add_followers(self):
        if not self.env.user.email:
            raise UserError(
                _(
                    "Unable to post message, please configure the sender's email address."
                )
            )
        email_from = self.env.user.email_formatted
        for wizard in self:
            Model = self.env[wizard.res_model]
            document = Model.browse(wizard.res_id)

            # 过滤合作伙伴ID以获得新的关注者，避免向已经关注的合作伙伴发送电子邮件
            new_partners = wizard.partner_ids - document.sudo().message_partner_ids
            document.message_subscribe(partner_ids=new_partners.ids)

            model_name = self.env["ir.model"]._get(wizard.res_model).display_name
            # 如果选中选项且存在邮件，则发送电子邮件（不要发送无效邮件）
            if (
                wizard.send_mail and wizard.message and not wizard.message == "<br>"
            ):  # 删除邮件时，cleditor会保留一个<br>
                message = self.env["mail.message"].create(
                    {
                        "subject": _(
                            "Invitation to follow %(document_model)s: %(document_name)s",
                            document_model=model_name,
                            document_name=document.display_name,
                        ),
                        "body": wizard.message,
                        "record_name": document.display_name,
                        "email_from": email_from,
                        "reply_to": email_from,
                        "model": wizard.res_model,
                        "res_id": wizard.res_id,
                        "reply_to_force_new": True,
                        "add_sign": True,
                    }
                )
                partners_data = []
                recipient_data = self.env["mail.followers"]._get_recipient_data(
                    document, "comment", False, pids=new_partners.ids
                )
                for pid, cid, active, pshare, ctype, notif, groups in recipient_data:
                    pdata = {
                        "id": pid,
                        "share": pshare,
                        "active": active,
                        "notif": "email",
                        "groups": groups or [],
                    }
                    if not pshare and notif:  # 有一个用户，但不是共享的，因此是用户
                        partners_data.append(dict(pdata, type="user"))
                    elif pshare and notif:  # 具有用户并且是共享的，因此是门户
                        partners_data.append(dict(pdata, type="portal"))
                    else:  # 没有用户，因此是客户
                        partners_data.append(dict(pdata, type="customer"))

                document._notify_record_by_email(
                    message, partners_data, send_after_commit=False,
                )
                # 如果发生故障，Web 客户端必须知道消息已被删除才能丢弃相关的失败通知
                self.env["bus.bus"].sendone(
                    (self._cr.dbname, "res.partner", self.env.user.partner_id.id),
                    {"type": "deletion", "message_ids": message.ids},
                )
                message.unlink()

            if (
                wizard.send_wecom_message
                and wizard.message
                and not wizard.message == "<br>"
            ):  # 删除邮件时，cleditor会保留一个<br>
                # tools.html2plaintext
                message = self.env["mail.message"].create(
                    {
                        "subject": _(
                            "Invitation to follow %(document_model)s: %(document_name)s",
                            document_model=model_name,
                            document_name=document.display_name,
                        ),
                        "body": wizard.message,
                        "record_name": document.display_name,
                        "email_from": email_from,
                        "reply_to": email_from,
                        "model": wizard.res_model,
                        "res_id": wizard.res_id,
                        "reply_to_force_new": True,
                        "add_sign": True,
                        #
                        "is_wecom_message": True,
                        "msgtype": "markdown",
                        "enable_duplicate_check": True,
                        "duplicate_check_interval": 1800,
                    }
                )

                partners_data = []
                recipient_data = self.env["mail.followers"]._get_recipient_data(
                    document, "comment", False, pids=new_partners.ids
                )
                partners_data = []
                recipient_data = self.env["mail.followers"]._get_recipient_data(
                    document, "comment", False, pids=new_partners.ids
                )
                for pid, active, pshare, notif, groups in recipient_data:
                    pdata = {
                        "id": pid,
                        "share": pshare,
                        "active": active,
                        "notif": "email",
                        "groups": groups or [],
                    }
                    if not pshare and notif:  # 有一个用户，但不是共享的，因此是用户
                        partners_data.append(dict(pdata, type="user"))
                    elif pshare and notif:  # 具有用户并且是共享的，因此是门户
                        partners_data.append(dict(pdata, type="portal"))
                    else:  # 没有用户，因此是客户
                        partners_data.append(dict(pdata, type="customer"))

                document._notify_record_by_wecom(message, partners_data, msg_vals=False)
                # message.unlink()
        return {"type": "ir.actions.act_window_close"}

# -*- coding: utf-8 -*-
"""
Author: PaulLei
Website: http://www.168nz.cn
Date: 2021-11-11 15:59:11
LastEditTime: 2021-11-12 23:01:05
LastEditors: PaulLei
Description: Description
"""
from odoo import _, api, fields, models
import json
from werkzeug import urls
import html2text


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _notify_record_by_inbox(
        self, message, recipients_data, msg_vals=False, **kwargs
    ):
        """
        使用企业微信通知partner,同时取消系统内的消息通知。
        """
        self._notify_record_by_wxwork(message, recipients_data, msg_vals, **kwargs)
        recipients_data["partners"] = []
        return super()._notify_record_by_inbox(
            message, recipients_data, msg_vals, **kwargs
        )

    def _notify_record_by_wxwork(
        self, message, recipients_data, msg_vals=False, **kwargs
    ):
        inbox_pids = [
            r["id"] for r in recipients_data["partners"] if r["notif"] == "inbox"
        ]
        wecom_ids = [
            p.wecom_id for p in self.env["res.partner"].browse(inbox_pids) if p.wecom_id
        ]
        msg_vals = {}
        if wecom_ids:
            wecom_template_id = self.env["wecom.message.template"].get_template_by_code(
                "notification"
            )
            bodies_text = self.env["mail.render.mixin"]._render_template(
                wecom_template_id.body_not_html,
                message._name,
                message.ids,
                post_process=True,
            )
            msg_vals.update(json.loads(bodies_text[message.id], strict=False))
            IrWxWorkMessageApi = self.env["wecom.message.api"]
            msg = IrWxWorkMessageApi.build_message(
                msgtype=wecom_template_id.msgtype,
                toall="",
                touser="|".join(wecom_ids),
                toparty="",
                totag="",
                subject=message.subject,
                media_id=wecom_template_id.media_id,
                description="描述",
                author_id=message.author_id,
                body_html="",
                body_json=bodies_text[message.id],
                safe=wecom_template_id.safe,
                enable_id_trans=wecom_template_id.enable_id_trans,
                enable_duplicate_check=wecom_template_id.enable_duplicate_check,
                duplicate_check_interval=wecom_template_id.duplicate_check_interval,
                company=self.env.company,
            )

            try:
                res = IrWxWorkMessageApi.send_by_api(msg)
            except AssertionError as error:
                pass


class MailMessage(models.Model):
    _inherit = "mail.message"

    access_link = fields.Char(string="消息链接", compute="_compute_access_link")
    company_id = fields.Many2one(
        "res.company", string="公司", default=lambda self: self.env.company
    )
    body_text = fields.Char(string="消息内容", compute="_compute_body_text")

    @api.depends("body")
    def _compute_body_text(self):
        for record in self:
            record.body_text = html2text.html2text(record.body)

    @api.depends("model", "res_id")
    def _compute_access_link(self):
        for record in self:
            if record.model and record.res_id:
                record.access_link = self._notify_get_action_link(
                    link_type="view", model=record.model, res_id=record.res_id
                )
            else:
                record.access_link = False

    def _notify_get_action_link(self, link_type, **kwargs):
        """Prepare link to an action: view document, follow document, ..."""
        params = {
            "model": kwargs.get("model", self._name),
            "res_id": kwargs.get("res_id", self.ids and self.ids[0] or False),
        }
        # whitelist accepted parameters: action (deprecated), token (assign), access_token
        # (view), auth_signup_token and auth_login (for auth_signup support)
        params.update(
            dict(
                (key, value)
                for key, value in kwargs.items()
                if key
                in (
                    "action",
                    "token",
                    "access_token",
                    "auth_signup_token",
                    "auth_login",
                )
            )
        )

        if link_type in ["view", "assign", "follow", "unfollow"]:
            base_link = "/mail/%s" % link_type
        elif link_type == "controller":
            controller = kwargs.get("controller")
            params.pop("model")
            base_link = "%s" % controller
        else:
            return ""

        if link_type not in ["view"]:
            token = self._notify_encode_link(base_link, params)
            params["token"] = token

        link = "%s?%s" % (base_link, urls.url_encode(params))
        if self:
            link = self[0].get_base_url() + link

        return link

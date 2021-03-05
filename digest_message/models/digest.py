# -*- coding: utf-8 -*-

import logging
from datetime import datetime, date
from werkzeug.urls import url_join
from odoo import api, fields, models, tools, _
from odoo.addons.base.models.ir_mail_server import MailDeliveryException

_logger = logging.getLogger(__name__)


class Digest(models.Model):
    _inherit = "digest.digest"

    # ------------------------------------------------------------
    # ACTIONS
    # ------------------------------------------------------------
    def _action_send_to_user(self, user, tips_count=1, consum_tips=True):
        web_base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")

        rendered_body = self.env["mail.render.mixin"]._render_template(
            "digest.digest_mail_main",
            "digest.digest",
            self.ids,
            engine="qweb",
            add_context={
                "title": self.name,
                "top_button_label": _("Connect"),
                "top_button_url": url_join(web_base_url, "/web/login"),
                "company": user.company_id,
                "user": user,
                "tips_count": tips_count,
                "formatted_date": datetime.today().strftime("%B %d, %Y"),
                "display_mobile_banner": True,
                "kpi_data": self.compute_kpis(user.company_id, user),
                "tips": self.compute_tips(
                    user.company_id, user, tips_count=tips_count, consumed=consum_tips
                ),
                "preferences": self.compute_preferences(user.company_id, user),
            },
            post_process=True,
        )[self.id]
        full_mail = self.env["mail.render.mixin"]._render_encapsulate(
            "digest.digest_mail_layout",
            rendered_body,
            add_context={"company": user.company_id, "user": user,},
        )
        # 根据值创建一个mail_mail，不带附件
        mail_values = {
            "subject": "%s: %s" % (user.company_id.name, self.name),
            "email_from": self.company_id.partner_id.email_formatted
            if self.company_id
            else self.env.user.email_formatted,
            "email_to": user.email_formatted,
            "body_html": full_mail,
            "auto_delete": True,
        }
        mail = self.env["mail.mail"].sudo().create(mail_values)
        mail.send(raise_exception=False)
        return True


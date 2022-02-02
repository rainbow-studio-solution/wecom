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
                "display_mobile_banner": False if user.wecom_userid else True,
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
        # 获取素材

        material_id = self.env["ir.model.data"].get_object_reference(
            "wecom_material", "wecom_material_image_kpi"
        )[1]
        material_template = self.env["wecom.material"].browse(material_id)

        material = self.env["wecom.material"].search(
            [
                ("name", "=", material_template.name),
                ("company_id", "=", user.company_id.id),
            ],
            limit=1,
        )

        if material:
            pass
        else:
            # 不存在 素材，复制 material 且 赋值 company_id
            copy_material = dict(
                name=material_template.name,
                media_type=material_template.media_type,
                temporary=material_template.temporary,
                media_file=material_template.media_file,
                media_filename=material_template.media_filename,
                company_id=user.company_id.id,
            )
            material = material_template.copy(copy_material)

        # if user.wecom_id:
        #     is_wecom_message = True
        # else:
        #     is_wecom_message = False

        # 根据值创建一个mail_mail，不带附件
        mail_values = {
            "subject": "%s: %s" % (user.company_id.name, self.name),
            "email_from": self.company_id.partner_id.email_formatted
            if self.company_id
            else self.env.user.email_formatted,
            "email_to": user.email_formatted,
            "auto_delete": True,
            # "is_wecom_message": is_wecom_message,
            "message_to_user": user.wecom_userid,
            "msgtype": "mpnews",
            "body_html": full_mail,
            "media_id": material.id,
            # "message_body_html": full_mail,
            "safe": "1",
            "enable_id_trans": False,
            "enable_duplicate_check": False,
            "duplicate_check_interval": 1800,
        }
        mail = self.env["mail.mail"].sudo().create(mail_values)
        mail.send_wecom_message(
            raise_exception=False, company=user.company_id,
        )
        return True


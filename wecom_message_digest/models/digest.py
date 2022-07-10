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
        get_param = self.env["ir.config_parameter"].sudo().get_param
        web_base_url = get_param("web.base.url")
        message_sending_method = get_param("wecom.message_sending_method")

        
        rendered_body = self.env['mail.render.mixin'].with_context(preserve_comments=True)._render_template(
            'digest.digest_mail_main',
            'digest.digest',
            self.ids,
            engine='qweb_view',
            add_context={
                'title': self.name,
                'top_button_label': _('Connect'),
                'top_button_url': self.get_base_url(),
                'company': user.company_id,
                'user': user,
                'unsubscribe_token': self._get_unsubscribe_token(user.id),
                'tips_count': tips_count,
                'formatted_date': datetime.today().strftime('%B %d, %Y'),
                # 'display_mobile_banner': True,
                'display_mobile_banner': False if user.wecom_userid else True,
                'kpi_data': self._compute_kpis(user.company_id, user),
                'tips': self._compute_tips(user.company_id, user, tips_count=tips_count, consumed=consum_tips),
                'preferences': self._compute_preferences(user.company_id, user),
            },
            post_process=True
        )[self.id]

        full_mail = self.env['mail.render.mixin']._render_encapsulate(
            'digest.digest_mail_layout',
            rendered_body,
            add_context={
                'company': user.company_id,
                'user': user,
            },
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

        # 创建基于值的mail_mail，无需附件
        mail_values = {
            'auto_delete': True,
            'author_id': self.env.user.partner_id.id,
            'email_from': self.company_id.partner_id.email_formatted if self.company_id else self.env.user.email_formatted,
            'email_to': user.email_formatted,
            'body_html': full_mail,
            'state': 'outgoing',
            'subject': '%s: %s' % (user.company_id.name, self.name),
            # 以下为企微字段
            "is_wecom_message":True if user.wecom_userid else False, 
            "message_to_user": user.wecom_userid,
            "msgtype": "mpnews",
            "body_html": full_mail,
            "media_id": material.id,
            "safe": "1",
            "enable_id_trans": False,
            "enable_duplicate_check": False,
            "duplicate_check_interval": 1800,
        }
        mail = self.env['mail.mail'].sudo().create(mail_values)
        if mail.is_wecom_message:
            mail.send_wecom_mail_message(
                raise_exception=False,
                company=user.company_id,
            )
        return True
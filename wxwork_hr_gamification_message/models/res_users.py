# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Users(models.Model):
    _inherit = "res.users"

    def _rank_changed(self):
        """
        可以在具有相同新等级的一批用户上调用的方法
        """
        template = self.env.ref(
            "gamification.mail_template_data_new_rank_reached", raise_if_not_found=False
        )
        if template:
            for u in self:
                if not u.wecom_id:
                    is_wecom_message = False
                else:
                    is_wecom_message = True
                if u.rank_id.karma_min > 0:
                    template.with_context(is_wecom_message=is_wecom_message).send_mail(
                        u.id,
                        force_send=False,
                        notif_layout="mail.mail_notification_light",
                    )

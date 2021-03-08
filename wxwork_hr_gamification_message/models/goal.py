# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
from odoo import api, fields, models, _, exceptions


class Goal(models.Model):
    """
    用户的目标实例 
    在指定时间段内用户的个人目标     
    """

    _inherit = "gamification.goal"

    # def _check_remind_delay(self):
    #     """Verify if a goal has not been updated for some time and send a
    #     reminder message of needed.

    #     :return: data to write on the goal object
    #     """
    #     if not (self.remind_update_delay and self.last_update):
    #         return {}

    #     delta_max = timedelta(days=self.remind_update_delay)
    #     last_update = fields.Date.from_string(self.last_update)
    #     if date.today() - last_update < delta_max:
    #         return {}

    #     # 生成提醒报告
    #     body_html = self.env.ref(
    #         "gamification.email_template_goal_reminder"
    #     )._render_field("body_html", self.ids, compute_lang=True)[self.id]
    #     message_body_html = self.env.ref(
    #         "gamification.email_template_goal_reminder"
    #     )._render_field("message_body_html", self.ids, compute_lang=True)[self.id]

    #     self.message_notify(
    #         body=body_html,
    #         message_body_html=message_body_html,
    #         partner_ids=[self.user_id.partner_id.id],
    #         subtype_xmlid="mail.mt_comment",
    #         email_layout_xmlid="mail.mail_notification_light",
    #     )

    #     return {"to_update": True}


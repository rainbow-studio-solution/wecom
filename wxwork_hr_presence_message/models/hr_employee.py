# -*- coding: utf-8 -*-

import logging

from ast import literal_eval
from odoo import fields, models, _, api
from odoo.exceptions import UserError
from odoo.fields import Datetime

_logger = logging.getLogger(__name__)


class Employee(models.AbstractModel):
    _inherit = "hr.employee.base"

    def action_send_mail(self):
        self.ensure_one()
        if not self.env.user.has_group("hr.group_hr_manager"):
            raise UserError(
                _(
                    "You don't have the right to do this. Please contact an Administrator."
                )
            )
        if not self.work_email:
            raise UserError(
                _("There is no professional email address for this employee.")
            )
        template = self.env.ref("hr_presence.mail_template_presence", False)
        compose_form = self.env.ref("mail.email_compose_message_wizard_form", False)
        ctx = dict(
            default_model="hr.employee",
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template.id,
            default_composition_mode="comment",
            default_is_log=True,
            custom_layout="mail.mail_notification_light",
        )
        return {
            "name": _("Compose Email"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(compose_form.id, "form")],
            "view_id": compose_form.id,
            "target": "new",
            "context": ctx,
        }

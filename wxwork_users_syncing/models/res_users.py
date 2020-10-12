# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from ...wxwork_api.helper.common import *
from odoo.exceptions import UserError


class Users(models.Model):
    _inherit = "res.users"
    _description = "Enterprise WeChat system users"
    _order = "wxwork_user_order"

    notification_type = fields.Selection(
        [("wxwork", "Handle by Enterprise WeChat")], default="mail", required=True,
    )

    wxwork_id = fields.Char(string="Enterprise WeChat user ID", readonly=True,)
    is_wxwork_notice = fields.Boolean("Whether to receive reminders", default=True,)
    is_wxwork_user = fields.Boolean("Is an enterprise WeChat user", readonly=True,)
    # qr_code = fields.Binary(string='个人二维码', help='员工个人二维码，扫描可添加为外部联系人', readonly=True)
    wxwork_user_order = fields.Char(
        "Enterprise WeChat ranking",
        default="0",
        help="The sort value in the department, the default is 0. The number must be the same as the department. The larger the number, the higher the order.The value range is [0, 2^32)",
        readonly=True,
    )


# ----------------------------------------------------------
# 变更用户类型向导
# ----------------------------------------------------------


class ChangeTypeWizard(models.TransientModel):
    _name = "wizard.change.user.type"
    _description = "Wizard to change user type(Enterprise WeChat)"

    def _default_user_ids(self):
        user_ids = (
            self._context.get("active_model") == "res.users"
            and self._context.get("active_ids")
            or []
        )
        return [
            (
                0,
                0,
                {"user_id": user.id, "user_login": user.login, "user_name": user.name,},
            )
            for user in self.env["res.users"].browse(user_ids)
        ]

    user_ids = fields.One2many(
        "user.type.change", "wizard_id", string="user", default=_default_user_ids
    )

    def change_type_button(self):
        self.ensure_one()
        self.user_ids.change_type_button()
        if self.env.user in self.mapped("user_ids.user_id"):
            return {"type": "ir.actions.client", "tag": "reload"}
        return {"type": "ir.actions.act_window_close"}


class ChangeTypeUser(models.TransientModel):
    _name = "user.type.change"
    _description = "User, Change Type Wizard"

    wizard_id = fields.Many2one(
        "wizard.change.user.type", string="Wizard", required=True, ondelete="cascade"
    )
    user_id = fields.Many2one(
        "res.users", string="User", required=True, ondelete="cascade"
    )
    user_login = fields.Char(string="Login account", readonly=True, translate=True,)
    user_name = fields.Char(string="Login name", readonly=True)
    choices = [("1", _("Internal User")), ("8", _("Portal")), ("9", _("Public"))]
    new_type = fields.Selection(
        choices, string="User Type", default="1", tracking=True, translate=True,
    )

    def change_type_button(self):
        for line in self:
            if not line.new_type:
                raise UserError(
                    _(
                        "Before clicking the 'Change User Type' button, you must modify the new user type"
                    )
                )
            if (
                line.user_id.id == 1
                or line.user_id.id == 2
                or line.user_id.id == 3
                or line.user_id.id == 4
                or line.user_id.id == 5
            ):
                pass
            else:
                line.user_id.write({"groups_id": [(6, 0, line.new_type)]})
        self.write({"new_type": False})

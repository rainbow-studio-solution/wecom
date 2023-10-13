# -*- coding: utf-8 -*-

import json
from odoo import api, fields, models, tools, _
from odoo.addons.base.models.res_users import check_identity


class ResUsers(models.Model):
    _inherit = "res.users"

    lock_screen = fields.Boolean(string="Lock Screen", default=False)

    theme_id = fields.Many2one(
        "res.theme", string="Theme", store=True, domain="[('user_id', '=', id)]"
    )

    # ------------------------------------------------------------
    # 1.main
    # ------------------------------------------------------------
    main_open_action_in_tabs = fields.Boolean(
        related="theme_id.main_open_action_in_tabs", readonly=False
    )
    main_submenu_position = fields.Selection(
        related="theme_id.main_submenu_position",
        readonly=False,
    )

    # ------------------------------------------------------------
    # 2.layout
    # ------------------------------------------------------------
    menu_layout_mode = fields.Selection(
        related="theme_id.menu_layout_mode", readonly=False
    )

    # ------------------------------------------------------------
    # 3.Theme color
    # ------------------------------------------------------------
    theme_color = fields.Selection(
        related="theme_id.theme_color", readonly=False
    )

    # ------------------------------------------------------------
    # 4.SideNavbar
    # ------------------------------------------------------------
    sidebar_display_number_of_submenus = fields.Boolean(
        related="theme_id.sidebar_display_number_of_submenus", readonly=False
    )
    sidebar_fixed = fields.Boolean(related="theme_id.sidebar_fixed", readonly=False)
    sidebar_show_minimize_button = fields.Boolean(
        related="theme_id.sidebar_show_minimize_button", readonly=False
    )
    sidebar_default_minimized = fields.Boolean(
        related="theme_id.sidebar_default_minimized", readonly=False
    )
    sidebar_hover_maximize = fields.Boolean(
        related="theme_id.sidebar_hover_maximize", readonly=False
    )

    # ------------------------------------------------------------
    # 6.Views
    # ------------------------------------------------------------
    display_scroll_top_button = fields.Boolean(related="theme_id.display_scroll_top_button", readonly=False)
    list_herder_fixed = fields.Boolean(related="theme_id.list_herder_fixed", readonly=False)
    list_rows_limit = fields.Selection(related="theme_id.list_rows_limit", readonly=False)
    form_chatter_position = fields.Selection(related="theme_id.form_chatter_position", readonly=False)

    # ------------------------------------------------------------
    # 7.Footer
    # ------------------------------------------------------------
    display_footer = fields.Boolean(related="theme_id.display_footer", readonly=False)
    display_footer_copyright = fields.Boolean(related="theme_id.display_footer_copyright", readonly=False)
    display_footer_document = fields.Boolean(related="theme_id.display_footer_document", readonly=False)
    display_footer_support = fields.Boolean(related="theme_id.display_footer_support", readonly=False)

    @api.model
    def set_user_theme(self, uid, theme):
        """
        为当前用户设置主题。
        """
        DATA_TYPE_LIST = ["main_submenu_position", "menu_layout_mode", "theme_color", "form_chatter_position"]

        for key, value in theme.items():
            if key in DATA_TYPE_LIST:
                theme[key] = str(value)

        result = {}
        try:
            user = self.browse(uid)
            user.theme_id.sudo().write(theme)  # type: ignore
        except Exception as e:
            result = {
                "state": False,
                "title": _("Theme setting failed!"),
                "message": str(e),
            }
        else:
            result = {
                "state": True,
                "title": _("Theme set successfully!"),
                "message": _(
                    "The theme is set successfully, Click the 'Refresh' button to load the new theme."
                ),
            }
        finally:
            return result

    @api.model_create_multi
    def create(self, vals_list):
        """
        创建新用户时，创建主题
        """
        users = super(ResUsers, self).create(vals_list)
        for new_user in users:
            new_user.theme_id = (   # type: ignore
                self.env["res.theme"].sudo()._get_or_create_theme(new_user.id, "user") # type: ignore
            )
        return users

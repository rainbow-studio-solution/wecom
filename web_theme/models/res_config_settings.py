# -*- coding: utf-8 -*-

import json
import logging
import base64
import io

from odoo.tools.misc import file_open
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.modules.module import get_resource_path
from random import randrange
from PIL import Image


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )

    # 品牌设置
    system_name = fields.Char(
        string="System Name",
        readonly=False,
        config_parameter="web_theme.system_name",
        default="iERP",
    )
    display_company_name = fields.Boolean(
        string="Display Company Name",
        default=False,
        config_parameter="web_theme.display_company_name",
    )
    logo = fields.Binary(related="company_id.logo", readonly=False)
    square_logo = fields.Binary(related="company_id.square_logo", readonly=False)
    favicon = fields.Binary(related="company_id.favicon", readonly=False)
    copyright = fields.Char(related="company_id.copyright", readonly=False)
    documentation_url = fields.Char(
        related="company_id.documentation_url", readonly=False
    )
    support_url = fields.Char(related="company_id.support_url", readonly=False)

    # 主题定制
    disable_theme_customizer = fields.Boolean(
        related="company_id.disable_theme_customizer", readonly=False
    )

    # ------------------------------------------------------------
    # 1.main
    # ------------------------------------------------------------
    main_submenu_position = fields.Selection(
        related="company_id.main_submenu_position", readonly=False
    )

    # ------------------------------------------------------------
    # 2.layout
    # ------------------------------------------------------------
    menu_layout_mode = fields.Selection(
        related="company_id.menu_layout_mode", readonly=False
    )

    # ------------------------------------------------------------
    # 3.Theme color
    # ------------------------------------------------------------
    theme_color = fields.Selection(related="company_id.theme_color", readonly=False)

    # ------------------------------------------------------------
    # 4.SideNavbar
    # ------------------------------------------------------------
    sidebar_display_number_of_submenus = fields.Boolean(
        related="company_id.sidebar_display_number_of_submenus", readonly=False
    )
    sidebar_fixed = fields.Boolean(related="company_id.sidebar_fixed", readonly=False)
    sidebar_show_minimize_button = fields.Boolean(
        related="company_id.sidebar_show_minimize_button", readonly=False
    )
    sidebar_default_minimized = fields.Boolean(
        related="company_id.sidebar_default_minimized", readonly=False
    )
    sidebar_hover_maximize = fields.Boolean(
        related="company_id.sidebar_hover_maximize", readonly=False
    )

    # ------------------------------------------------------------
    # 6.Views
    # ------------------------------------------------------------
    display_scroll_top_button = fields.Boolean(
        related="company_id.display_scroll_top_button", readonly=False
    )
    list_herder_fixed = fields.Boolean(
        related="company_id.list_herder_fixed", readonly=False
    )
    list_rows_limit = fields.Selection(
        related="company_id.list_rows_limit", readonly=False
    )
    form_chatter_position = fields.Selection(
        related="company_id.form_chatter_position", readonly=False
    )

    # ------------------------------------------------------------
    # 7.Footer
    # ------------------------------------------------------------
    display_footer = fields.Boolean(related="company_id.display_footer", readonly=False)
    display_footer_copyright = fields.Boolean(
        related="company_id.display_footer_copyright", readonly=False
    )

    display_footer_document = fields.Boolean(
        related="company_id.display_footer_document", readonly=False
    )
    # footer_document_url = fields.Char(related="company_id.footer_document_url", readonly=False)
    display_footer_support = fields.Boolean(
        related="company_id.display_footer_support", readonly=False
    )
    # footer_support_url = fields.Char(related="company_id.footer_support_url", readonly=False)

    # 用户菜单
    enable_odoo_account = fields.Boolean(
        related="company_id.enable_odoo_account", readonly=False
    )
    enable_developer_tool = fields.Boolean(
        related="company_id.enable_developer_tool", readonly=False
    )

    enable_lock_screen = fields.Boolean(
        related="company_id.enable_lock_screen", readonly=False
    )
    lock_screen_state_storage_mode = fields.Selection(
        related="company_id.lock_screen_state_storage_mode", readonly=False
    )

    enable_documentation = fields.Boolean(
        related="company_id.enable_documentation", readonly=False
    )
    enable_support = fields.Boolean(related="company_id.enable_support", readonly=False)

    # def set_values(self):
    #     super().set_values()

    # def write(self, vals):
    #     ThemeConfig = super(ResConfigSettings, self).write(vals)
    #     if vals.get('footer_copyright') or vals.get('footer_copyright') or vals.get('footer_copyright'):
    #         print("修改了版权")
    #         print("  --------")
    #         # self._check_twitter_authorization()
    #     return ThemeConfig

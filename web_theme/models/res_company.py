# -*- coding: utf-8 -*-

import base64
from email.policy import default
import io
import os

from odoo import models, fields, api, tools, _
from odoo.modules.module import get_module_resource, get_resource_path
from random import randrange
from PIL import Image
import datetime


class ResCompany(models.Model):
    _inherit = "res.company"

    def _get_theme_favicon(self, original=False):
        img_path = get_resource_path("web_theme", "static/img/favicon.ico")
        with tools.file_open(img_path, "rb") as f:
            if original:
                return base64.b64encode(f.read())
            # Modify the source image to add a colored bar on the bottom
            # This could seem overkill to modify the pixels 1 by 1, but
            # Pillow doesn't provide an easy way to do it, and this
            # is acceptable for a 16x16 image.
            color = (
                randrange(32, 224, 24),
                randrange(32, 224, 24),
                randrange(32, 224, 24),
            )
            original = Image.open(f)
            new_image = Image.new("RGBA", original.size)
            height = original.size[1]
            width = original.size[0]
            bar_size = 1
            for y in range(height):
                for x in range(width):
                    pixel = original.getpixel((x, y))
                    if height - bar_size <= y + 1 <= height:
                        new_image.putpixel((x, y), (color[0], color[1], color[2], 255))
                    else:
                        new_image.putpixel(
                            (x, y), (pixel[0], pixel[1], pixel[2], pixel[3])
                        )
            stream = io.BytesIO()
            new_image.save(stream, format="ICO")
            return base64.b64encode(stream.getvalue())

    def _default_theme(self):
        return self.env["res.theme"].sudo()._get_or_create_theme(self.id, "company")  # type: ignore

    def _get_square_logo(self):
        img_path = get_module_resource("web_theme", "static", "img", "square_logo.png")
        return base64.b64encode(open(img_path, "rb").read())

    square_logo = fields.Binary(
        default=_get_square_logo,
        # related="partner_id.image_1920",
        string="Company Square Logo",
        readonly=False,
    )
    square_logo_web = fields.Binary(
        compute="_compute_square_logo_web", store=True, attachment=False
    )

    @api.depends("square_logo")
    def _compute_square_logo_web(self):
        for company in self:
            img = company.square_logo  # type: ignore
            company.square_logo_web = img and base64.b64encode(  # type: ignore
                tools.image_process(base64.b64decode(img), size=(180, 0))  # type: ignore
            )

    theme_id = fields.Many2one(
        "res.theme",
        string="Theme",
        store=True,
        domain="[('company_id', '=', id)]",
    )
    disable_theme_customizer = fields.Boolean(
        string="Disable theme customizer",
        related="theme_id.disable_theme_customizer",
        readonly=False,
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
    theme_color = fields.Selection(related="theme_id.theme_color", readonly=False)

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
    display_scroll_top_button = fields.Boolean(
        related="theme_id.display_scroll_top_button", readonly=False
    )
    list_herder_fixed = fields.Boolean(
        related="theme_id.list_herder_fixed", readonly=False
    )
    list_rows_limit = fields.Selection(
        related="theme_id.list_rows_limit", readonly=False
    )
    form_chatter_position = fields.Selection(
        related="theme_id.form_chatter_position", readonly=False
    )

    # ------------------------------------------------------------
    # 7.Footer
    # ------------------------------------------------------------
    display_footer = fields.Boolean(related="theme_id.display_footer", readonly=False)
    display_footer_copyright = fields.Boolean(
        related="theme_id.display_footer_copyright", readonly=False
    )
    display_footer_document = fields.Boolean(
        related="theme_id.display_footer_document", readonly=False
    )
    display_footer_support = fields.Boolean(
        related="theme_id.display_footer_support", readonly=False
    )

    # 用户菜单
    menuitem_id = fields.Many2one(
        "res.user.menuitems",
        string="User menu items",
        store=True,
        domain="[('company_id', '=', id)]",
    )
    enable_odoo_account = fields.Boolean(
        related="menuitem_id.enable_odoo_account", readonly=False
    )
    enable_lock_screen = fields.Boolean(
        related="menuitem_id.enable_lock_screen", readonly=False
    )
    lock_screen_state_storage_mode = fields.Selection(
        string="Lock screen state storage mode",
        selection=[
            ("1", "Use browser's local storage"),
            ("2", "Use database"),
        ],
        default="1",
    )
    enable_developer_tool = fields.Boolean(
        related="menuitem_id.enable_developer_tool", readonly=False
    )
    enable_documentation = fields.Boolean(
        related="menuitem_id.enable_documentation", readonly=False
    )
    enable_support = fields.Boolean(
        related="menuitem_id.enable_support", readonly=False
    )

    # 版权的文本内容 ， 文档 / 技术支持 的URL
    def _get_default_copyright(self):
        """
        年份© 公司名称
        """
        return "%s© %s" % (datetime.datetime.today().year,(self.name if self.name else 'Odoo') )  # type: ignore

    copyright = fields.Char(string="Copyright", default=_get_default_copyright)
    documentation_url = fields.Char(
        string="Documentation URL", default="https://eis.wiki"
    )
    support_url = fields.Char(string="Support URL", default="https://eis.hb.cn/")

    @api.model_create_multi
    def create(self, vals_list):
        """
        创建新公司时，创建主题 和 用户菜单项目
        """
        companies = super(ResCompany, self).create(vals_list)
        for new_company in companies:
            new_company.theme_id = (  # type: ignore
                self.env["res.theme"]
                .sudo()
                ._get_or_create_theme(new_company.id, "company")  # type: ignore
            )

            new_company.menuitem_id = (  # type: ignore
                self.env["res.user.menuitems"]
                .sudo()
                ._get_or_create_menuitems(new_company.id)  # type: ignore
            )

        return companies

    # def write(self, vals):
    #     """
    #     修改公司的版权信息、文档URL、技术支持URL时，
    #     同时设置默认该公司的所有系统用户的 版权信息、文档URL、技术支持URL
    #     """
    #     ThemeConfig = super(ResCompany, self).write(vals)
    #     if vals.get('copyright') or vals.get('copyright') or vals.get('copyright'):
    #         users = self.env["res.users"].search([("company_id","=",self.id )]) # type: ignore
    #         for user in users:
    #             user.write({
    #                 "copyright":vals.get('copyright')
    #             })

    #     if vals.get('documentation_url') or vals.get('documentation_url') or vals.get('documentation_url'):
    #         users = self.env["res.users"].search([("company_id","=",self.id )]) # type: ignore
    #         for user in users:
    #             user.write({
    #                 "documentation_url":vals.get('documentation_url')
    #             })

    #     if vals.get('support_url') or vals.get('support_url') or vals.get('support_url'):
    #         users = self.env["res.users"].search([("company_id","=",self.id )]) # type: ignore
    #         for user in users:
    #             user.write({
    #                 "support_url":vals.get('support_url')
    #             })

    #     return ThemeConfig

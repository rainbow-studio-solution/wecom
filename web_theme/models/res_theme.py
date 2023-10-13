# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import datetime

class ResTheme(models.Model):
    _name = "res.theme"
    _description = "Theme"

    name = fields.Char(
        string="Name",
        copy=False,
        compute="_compute_name",
        store=True,
        index=True,
    )  # 企业应用名称

    company_id = fields.Many2one(
        string="Company", comodel_name="res.company", ondelete="cascade", readonly=True
    )
    user_id = fields.Many2one(
        string="User", comodel_name="res.users", ondelete="cascade", readonly=True
    )

    type = fields.Selection(
        string="Type",
        selection=[("user", "User"), ("company", "Company")],
        required=True,
        # compute="_compute_company_type",
        # inverse="_write_company_type",
    )

    disable_theme_customizer = fields.Boolean(
        string="Disable theme customizer", default=False
    )
    # ------------------------------------------------------------
    # 版权的文本内容 ， 文档 / 技术支持 的URL
    # ------------------------------------------------------------
    copyright = fields.Char(related="company_id.copyright", readonly=False)
    documentation_url = fields.Char(related="company_id.documentation_url", readonly=False)
    support_url = fields.Char(related="company_id.support_url", readonly=False)

    # ------------------------------------------------------------
    # 1.main
    # ------------------------------------------------------------
    main_open_action_in_tabs = fields.Boolean(string="Open action in tabs", default=False) #multiple open page in tab
    main_submenu_position = fields.Selection(
        string="Submenu Position",
        selection=[
            ("1", "Header Navbar Menu"),
            ("2", "Sidebar Navbar Menu"),
            ("3", "Header and Sidebar Navbar Menu"),
        ],
        default="3",
        required=True,
        readonly=False,
    )

    # ------------------------------------------------------------
    # 2.layout
    # ------------------------------------------------------------
    menu_layout_mode = fields.Selection(
        string="Menu layout mode",
        selection=[
            ("1", "Sidebar Menu Mode"),
            ("2", "Favorites Menu Mode"),
            ("3", "Drawer Menu Mode"),
        ],
        default="1",
        required=True,
        readonly=False,
    )  # ("2", "Favorites"), ("3", "Drawer")

    # ------------------------------------------------------------
    # 3.Favorites Menu
    # ------------------------------------------------------------
    # ------------------------------------------------------------
    # 4.Drawer Menu
    # ------------------------------------------------------------

    # ------------------------------------------------------------
    # 5.Theme color
    # ------------------------------------------------------------
    theme_color = fields.Selection(
        string="Theme color",
        selection=[
            ("default", "Light Blue"),
            ("darkblue", "Dark Blue"),
            ("purple", "Purple"),
            ("deep_purple", "Deep purple"),
            ("grey", "Grey"),
            ("light", "Light"),
            ("light2", "Light2"),
        ],
        default="default",
        required=True,
        readonly=False,
    )

    # ------------------------------------------------------------
    # 6.SideNavbar
    # ------------------------------------------------------------
    sidebar_display_number_of_submenus = fields.Boolean(
        string="Display Number Of Submenus", default=True
    )
    sidebar_fixed = fields.Boolean(string="Fixed SideNavbar", default=True)
    sidebar_show_minimize_button = fields.Boolean(
        string="Show minimize button", default=True
    )
    sidebar_default_minimized = fields.Boolean(string="Default minimize", default=False)
    sidebar_hover_maximize = fields.Boolean("Hover maximize", default=True)

    # ------------------------------------------------------------
    # 7.Hheader
    # ------------------------------------------------------------

    # ------------------------------------------------------------
    # 8.Views
    # ------------------------------------------------------------
    display_scroll_top_button = fields.Boolean(
        string="Display Scroll Top Button", default=True
    )
    list_herder_fixed = fields.Boolean(string="List Header Fixed", default=False)
    list_rows_limit = fields.Selection(string="Number of rows in the list", selection=[
            ("80", "80 rows"),
            ("100", "100 rows"),
            ("120", "120 rows"),
            ("140", "140 rows"),
            ("160", "160 rows"),
            ("180", "180 rows"),
            ("200", "200 rows"),
        ],default="80", required=True)
    form_chatter_position = fields.Selection(
        string="Form Chatter Position",
        selection=[
            ("1", "Right side of the form"),
            ("2", "Bottom of form"),
        ],
        default="1",
        required=True,
        readonly=False,
    )

    # ------------------------------------------------------------
    # 9.Footer
    # ------------------------------------------------------------
    display_footer = fields.Boolean(string="Display Footer", default=True)
    display_footer_copyright = fields.Boolean(string="Display footer copyright information", default=True)
    display_footer_document = fields.Boolean(string="Display footer document",default=True)
    display_footer_support = fields.Boolean(string="Display footer support",default=True)

    @api.depends("company_id", "user_id", "type")
    def _compute_name(self):
        for theme in self:
            labels = dict(self.fields_get(allfields=["type"])["type"]["selection"])[theme.type]  # type: ignore
            if theme.company_id:  # type: ignore
                theme.name = "%s:%s" % (labels, theme.company_id.name)  # type: ignore
            else:
                theme.name = "%s:%s" % (labels, theme.user_id.name)  # type: ignore




    def _get_or_create_theme(self, id, type):
        """
        通过id和type获取或者创建theme
        """
        domain = []
        vals = {}
        if type == "company":
            domain = [("company_id", "=", id), ("type", "=", "company")]
            vals = {"company_id": id, "type": "company"}
        elif type == "user":
            domain = [("user_id", "=", id), ("type", "=", "user")]
            vals = {"user_id": id, "type": "user"}
        theme = self.search(domain, limit=1)

        if not theme:
            theme = self.create(vals)

        return theme

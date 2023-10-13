# -*- coding: utf-8 -*-

import json
from odoo import api, models
from odoo.http import request
from odoo.tools import ustr


class Http(models.AbstractModel):
    _inherit = "ir.http"

    def webclient_rendering_context(self):
        """
        覆盖社区版,以防止不必要的加载请求
        """
        return {
            "session_info": self.session_info(),
        }

    def session_info(self):
        """
        设置用户的主题信息 和锁屏信息
        """
        session_info = super(Http, self).session_info()  # type: ignore
        del session_info["support_url"]

        ICP = self.env["ir.config_parameter"].sudo()
        system_name = ICP.get_param("web_theme.system_name", default="iERP")
        display_company_name = ICP.get_param(
            "web_theme.display_company_name", default=False
        )

        if type(display_company_name) == str and display_company_name.lower() in [
            "true",
            "t",
            "1",
        ]:
            display_company_name = True
        elif type(display_company_name) == str and display_company_name.lower() in [
            "false",
            "f",
            "0",
        ]:
            display_company_name = False

        # 用户菜单项
        current_conpany = self.env.user.company_id
        enable_odoo_account = current_conpany.enable_odoo_account
        enable_lock_screen = current_conpany.enable_lock_screen
        enable_developer_tool = current_conpany.enable_developer_tool
        enable_documentation = current_conpany.enable_documentation
        documentation_url = current_conpany.documentation_url
        enable_support = current_conpany.enable_support
        support_url = current_conpany.support_url

        # 语言
        # -------------------------------------------------------
        langs = self.env["res.lang"].search_read([], ["name", "code", "flag_image_url"])
        for lang in langs:
            if lang["code"] == request.env.lang:  # type: ignore
                session_info["current_lang"] = lang
                break
        session_info["langs"] = langs

        current_user = self.env.user
        current_user_company = current_user.company_id

        session_info.update(
            {
                "system_name": system_name,
                "enable_odoo_account": enable_odoo_account,
                "enable_lock_screen": enable_lock_screen,
                "enable_developer_tool": enable_developer_tool,
                "support": {
                    "support_url": support_url,
                    "hide": enable_support,
                },
                "documentation": {
                    "documentation_url": documentation_url,
                    "hide": enable_documentation,
                },
            }
        )
        if display_company_name:
            session_info.update({"display_company_name": display_company_name})

        # 主题
        # -------------------------------------------------------
        disable_theme_customizer = (
            current_user_company.theme_id.disable_theme_customizer
        )
        theme = {}

        theme_id = current_user.theme_id
        if disable_theme_customizer:
            # 如果关闭用户定制主题功能，则使用公司绑定的主题
            theme_id = current_user_company.theme_id

        # 1.MAIN
        main_submenu_position_dict = dict(
            self.env["res.theme"].fields_get("main_submenu_position")[
                "main_submenu_position"
            ]["selection"]
        )
        main_submenu_position_list = []
        for key, value in main_submenu_position_dict.items():
            mode = {"id": int(key), "name": value}
            if key == "1":
                mode.update(
                    {"icon": "/web_theme/static/img/submenu/submenu-header.png"}
                )
            if key == "2":
                mode.update(
                    {"icon": "/web_theme/static/img/submenu/submenu-sidebar.png"}
                )
            if key == "3":
                mode.update({"icon": "/web_theme/static/img/submenu/submenu-both.png"})
            main_submenu_position_list.append(mode)

        # 2. layout
        menu_layout_mode_dict = dict(
            self.env["res.theme"].fields_get("menu_layout_mode")["menu_layout_mode"][
                "selection"
            ]
        )

        menu_layout_mode_list = []
        for key, value in menu_layout_mode_dict.items():
            mode = {"id": int(key), "name": value}
            if key == "1":
                mode.update({"icon": "bi-window-sidebar"})
            if key == "2":
                mode.update({"icon": "bi-list-stars"})
            if key == "3":
                mode.update({"icon": "bi-window-dock"})
            menu_layout_mode_list.append(mode)

        # 3.Theme color
        theme_color_dict = dict(
            self.env["res.theme"].fields_get("theme_color")["theme_color"]["selection"]
        )
        theme_color_list = []
        for key, value in theme_color_dict.items():
            color = {"code": key, "name": value}
            if key == "default":
                color.update({"color": "#3975c6"})
            if key == "darkblue":
                color.update({"color": "#2b3643"})
            if key == "purple":
                color.update({"color": "#71639e"})
            if key == "deep_purple":
                color.update({"color": "#714B67"})
            if key == "grey":
                color.update({"color": "#697380"})
            if key == "light":
                color.update({"color": "#F9FAFD"})
            if key == "light2":
                color.update({"color": "#F1F1F1"})
            theme_color_list.append(color)

        # 6.Views
        views_form_chatter_position_dict = dict(
            self.env["res.theme"].fields_get("form_chatter_position")[
                "form_chatter_position"
            ]["selection"]
        )
        views_form_chatter_position_list = []
        for key, value in views_form_chatter_position_dict.items():
            mode = {"id": int(key), "name": value}
            if key == "1":
                mode.update({"icon": "bi-layout-sidebar-inset-reverse"})
            if key == "2":
                mode.update({"icon": "bi-text-wrap"})
            views_form_chatter_position_list.append(mode)

        views_list_rows_limit_dict = dict(
            self.env["res.theme"].fields_get("list_rows_limit")["list_rows_limit"][
                "selection"
            ]
        )
        views_list_rows_limit_list = []
        for key, value in views_list_rows_limit_dict.items():
            row = {"value": int(key), "name": value}
            views_list_rows_limit_list.append(row)

        # 7.Footer

        theme = {
            "disable_customization": disable_theme_customizer,
            "copyright": current_conpany.copyright,
            "support_url": support_url,
            "documentation_url": documentation_url,
            # 1.main
            "main_open_action_in_tabs": theme_id.main_open_action_in_tabs,
            "main_submenu_position": int(theme_id.main_submenu_position),
            "main_submenu_positions": main_submenu_position_list,
            # 2.layout
            "menu_layout_mode": int(theme_id.menu_layout_mode),
            "menu_layout_modes": menu_layout_mode_list,
            # 3.Theme color
            "theme_color": theme_id.theme_color,
            "theme_colors": theme_color_list,
            # 4.SideNavbar
            "sidebar_display_number_of_submenus": theme_id.sidebar_display_number_of_submenus,
            "sidebar_fixed": theme_id.sidebar_fixed,
            "sidebar_show_minimize_button": theme_id.sidebar_show_minimize_button,
            "sidebar_default_minimized": theme_id.sidebar_default_minimized,
            "sidebar_hover_maximize": theme_id.sidebar_hover_maximize,
            # 6.Views
            "display_scroll_top_button": theme_id.display_scroll_top_button,
            "list_herder_fixed": theme_id.list_herder_fixed,
            "list_rows_limit": int(theme_id.list_rows_limit),
            "list_rows_limits": views_list_rows_limit_list,
            "form_chatter_position": int(theme_id.form_chatter_position),
            "form_chatter_positions": views_form_chatter_position_list,
            # 7.Footer
            "display_footer": theme_id.display_footer,
            "display_footer_copyright": theme_id.display_footer_copyright,
            "display_footer_document": theme_id.display_footer_document,
            "display_footer_support": theme_id.display_footer_support,
        }
        session_info.update({"theme": json.loads(json.dumps(theme))})

        # 锁屏方式
        # -------------------------------------------------------
        session_info.update(
            {
                "lock_screen_state_storage_mode": int(
                    current_user_company.lock_screen_state_storage_mode
                ),
                # "lock_screen_state":False,
            }
        )
        # print(session_info)
        return session_info

    def get_frontend_session_info(self):
        session_info = super(Http, self).get_frontend_session_info()  # type: ignore

        # 锁屏方式
        session_info.update(
            {
                "lock_screen_state_storage_mode": int(
                    self.env.user.company_id.lock_screen_state_storage_mode
                ),
                # "lock_screen_state":False,
            }
        )

        return session_info

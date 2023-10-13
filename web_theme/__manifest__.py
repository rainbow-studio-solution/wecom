# -*- coding: utf-8 -*-

{
    "name": "iERP Backend Theme",
    "author": "RStudio",
    "website": "https://eis-solution.coding.net/public/odoo/oec/git",
    "sequence": 0,
    "installable": True,
    "application": True,
    "auto_install": False,
    "category": "iERP Suites/Backend",
    "version": "16.0.0.1",
    "summary": "Back-end theme extension",
    "description": """
Web Client.
===========================

This module modifies the web plug-in to provide the following functions:
---------------------------
1) Responsiveness
2) Sidebars
3) Supports more than four levels of menus
4) Scroll to top button
5) Support custom browser window title name
""",
    "depends": ["web", "mail", "calendar", "portal", "spreadsheet"],
    
    "excludes": [
        "web_enterprise",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_config_parameter.xml",
        "data/res_theme_data.xml",
        "data/res_company_data.xml",
        "views/partner_view.xml",
        "views/webclient_templates.xml",
        "views/res_company_views.xml",
        "views/res_users_views.xml",
        "views/res_groups_views.xml",
        "views/calendar_views.xml",
        "views/res_config_settings_views.xml",
        "views/configurator_views.xml",
    ],
    "assets": {
        "web._assets_primary_variables": [
            (
                "after",
                "web/static/src/scss/primary_variables.scss",
                "web_theme/static/src/**/**/*.variables.scss",
            ),
            (
                "before",
                "web/static/src/scss/primary_variables.scss",
                "web_theme/static/src/scss/primary_variables.scss",
            ),
        ],
        "web._assets_secondary_variables": [
            (
                "before",
                "web/static/src/scss/secondary_variables.scss",
                "web_theme/static/src/scss/secondary_variables.scss",
            ),
        ],
        "web._assets_backend_helpers": [
            (
                "before",
                "web/static/src/scss/bootstrap_overridden.scss",
                "web_theme/static/src/scss/bootstrap_overridden.scss",
            ),
        ],
        "web.assets_common": [
            "web_theme/static/fonts/fonts.scss",
            "web_theme/static/fonts/password.scss",
            "web_theme/static/libs/bootstrap-icons/bootstrap-icons.css",
            "web_theme/static/src/webclient/drawer_menu/drawer_menu_background.scss",
            "web_theme/static/src/webclient/navbar/navbar.scss",
        ],
        "web.assets_frontend": [
            "web_theme/static/src/webclient/drawer_menu/drawer_menu_background.scss",
            "web_theme/static/src/webclient/navbar/navbar.scss",
        ],
        "web.assets_backend": [
            # CSS replace
            (
                "replace",
                "web/static/src/webclient/webclient_layout.scss",
                "web_theme/static/src/webclient/webclient_layout.scss",
            ),
            (
                "replace",
                "web/static/src/legacy/scss/fields_extra.scss",
                "web_theme/static/src/legacy/scss/fields.scss",
            ),
            (
                "replace",
                "web/static/src/legacy/scss/form_view_extra.scss",
                "web_theme/static/src/legacy/scss/form_view.scss",
            ),
            (
                "replace",
                "web/static/src/legacy/scss/list_view_extra.scss",
                "web_theme/static/src/legacy/scss/list_view.scss",
            ),
            # js replace
            # ("replace","web/static/src/webclient/user_menu/user_menu_items.js","web_theme/static/src/webclient/user_menu/user_menu_items.js"),
            "web_theme/static/src/legacy/scss/dropdown.scss",
            "web_theme/static/src/legacy/scss/control_panel_mobile.scss",
            "web_theme/static/src/legacy/scss/kanban_view.scss",
            "web_theme/static/src/legacy/scss/touch_device.scss",
            "web_theme/static/src/legacy/scss/form_view_mobile.scss",
            "web_theme/static/src/legacy/scss/modal_mobile.scss",
            "web_theme/static/src/legacy/scss/promote_studio.scss",
            "web_theme/static/src/webclient/**/*.scss",
            (
                "remove",
                "web_theme/static/src/webclient/drawer_menu/drawer_menu_background.scss",
            ),  # already in _assets_common_styles
            (
                "remove",
                "web_theme/static/src/webclient/navbar/navbar.scss",
            ),  # already in _assets_common_styles
            "web_theme/static/src/views/**/*.scss",
            # Allows events to be added to the ListRenderer before it is extended.
            (
                "prepend",
                "web_theme/static/src/legacy/js/views/list/list_renderer_mobile.js",
            ),
            "web_theme/static/src/legacy/js/apps.js",
            "web_theme/static/src/core/**/*",
            "web_theme/static/src/webclient/**/*.js",
            "web_theme/static/src/webclient/**/*.xml",
            "web_theme/static/src/views/**/*.js",
            "web_theme/static/src/views/**/*.xml",
            "web_theme/static/src/legacy/**/*.js",
            "web_theme/static/src/legacy/**/*.xml",
            "web_theme/static/src/components/**/*",
            # Don"t include dark mode files in light mode
            ("remove", "web_theme/static/src/**/**/*.dark.scss"),
        ],
        "web.assets_backend_prod_only": [
            ("replace", "web/static/src/main.js", "web_theme/static/src/main.js"),
        ],
        # ========= Dark Mode =========
        "web.dark_mode_variables": [
            # web._assets_primary_variables
            (
                "before",
                "web_theme/static/src/scss/primary_variables.scss",
                "web_theme/static/src/scss/primary_variables.dark.scss",
            ),
            (
                "before",
                "web_theme/static/src/**/**/*.variables.scss",
                "web_theme/static/src/**/**/*.variables.dark.scss",
            ),
            # web._assets_secondary_variables
            (
                "before",
                "web_theme/static/src/scss/secondary_variables.scss",
                "web_theme/static/src/scss/secondary_variables.dark.scss",
            ),
        ],
        "web.dark_mode_assets_common": [
            ("include", "web.dark_mode_variables"),
        ],
        "web.dark_mode_assets_backend": [
            ("include", "web.dark_mode_variables"),
            # web._assets_backend_helpers
            (
                "before",
                "web_theme/static/src/scss/bootstrap_overridden.scss",
                "web_theme/static/src/scss/bootstrap_overridden.dark.scss",
            ),
            (
                "after",
                "web/static/lib/bootstrap/scss/_functions.scss",
                "web_theme/static/src/scss/bs_functions_overridden.dark.scss",
            ),
            # assets_backend
            "web_theme/static/src/**/**/*.dark.scss",
        ],
        # 锁屏样式
        "web.assets_lock": [
            "web/static/src/libs/fontawesome/css/font-awesome.css",
            "web/static/lib/bootstrap/dist/css/bootstrap.css",
            "web/static/lib/jquery/jquery.js",
            "web/static/lib/bootstrap/js/dist/dom/data.js",
            "web/static/lib/bootstrap/js/dist/dom/event-handler.js",
            "web/static/lib/bootstrap/js/dist/dom/manipulator.js",
            "web/static/lib/bootstrap/js/dist/dom/selector-engine.js",
            "web/static/lib/bootstrap/js/dist/base-component.js",
            "web/static/lib/bootstrap/js/dist/modal.js",
            "web_theme/static/libs/bootstrap-icons/bootstrap-icons.css",
            "web_theme/static/fonts/password.scss",
            "web_theme/static/src/lockclient/*",
        ],
        "mail.assets_discuss_public": [],
        "spreadsheet.o_spreadsheet": [
            "web_theme/static/src/spreadsheet/**/*",
        ],
    },
    "post_init_hook": "post_init_hook",  # 安装后执行的方法
    "license": "OEEL-1",
    "bootstrap": True,  # 加载登录屏幕的翻译，
}

# -*- coding: utf-8 -*-

{
    "name": "WeCom Base",
    "author": "RStudio",
    "sequence": 601,
    "installable": True,
    "application": True,
    "auto_install": False,
    "category": "WeCom/WeCom",
    "website": "https://gitee.com/rainbowstudio/wecom",
    "version": "15.0.0.1",
    "summary": """
        
        """,
    "description": """

        """,
    "depends": ["base_setup", "wecom_l10n", "wecom_widget", "wecom_api"],
    "data": [
        "security/wecom_security.xml",
        "security/ir.model.access.csv",
        "data/wecom_server_api_error_data.xml",
        "data/service_api_list_data.xml",
        "data/ir_module_category_data.xml",
        "data/ir_config_parameter.xml",
        "data/ir_cron_data.xml",
        "data/wecom_app_type_data.xml",
        # "data/wecom_apps_data.xml",
        # "data/wecom_app_config_data.xml",
        # "views/assets_templates.xml",
        "views/ir_cron_views.xml",
        "views/res_config_settings_views.xml",
        "views/res_company_views.xml",
        # "views/res_users_views.xml",
        "views/wecom_service_api_list_views.xml",
        "views/wecom_service_api_error_views.xml",
        "views/wecom_apps_views.xml",
        "views/wecom_app_config_views.xml",
        "views/wecom_app_callback_service_views.xml",
        "views/wecom_app_event_type_views.xml",
        "views/wecom_app_type_views.xml",
        "views/wecom_app_subtype_views.xml",
        "views/menu_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            # SCSSS
            "wecom_base/static/src/scss/wecom_settings_navigation.scss",
            # JS
            "wecom_base/static/src/js/wecom_settings_navigation.js",            
            "wecom_base/static/src/js/list_header_button.js",
        ],
        "web.assets_qweb": [
            "wecom_base/static/src/xml/*.xml",
        ],
    },
    "license": "LGPL-3",
    # "post_init_hook": "_open_wecom_settings",
}

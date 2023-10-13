# -*- coding: utf-8 -*-

{
    "name": "WeCom Base",
    "author": "RStudio",
    "sequence": 601,
    "installable": True,
    "application": True,
    "auto_install": False,
    "category": "WeCom Suites/Settings",
    "website": "https://gitee.com/rainbowstudio/wecom",
    "version": "16.0.0.1",
    "summary": """

        """,
    "description": """

        """,
    "depends": ["base_setup", "wecom_widget", "wecom_api"],
    "data": [
        "security/wecom_security.xml",
        "security/ir.model.access.csv",
        "data/ir_module_category_data.xml",
        "data/ir_config_parameter.xml",
        "data/ir_cron_data.xml",
        "data/wecom_app_type_data.xml",
        "views/ir_cron_views.xml",
        "views/res_config_settings_views.xml",
        "views/res_company_views.xml",
        "views/wecom_service_api_list_views.xml",
        "views/wecom_service_api_error_views.xml",
        "views/wecom_apps_views.xml",
        "views/wecom_app_config_views.xml",
        "views/wecom_app_callback_service_views.xml",
        "views/wecom_app_event_type_views.xml",
        "views/wecom_app_type_views.xml",
        "views/wecom_app_subtype_views.xml",
        "views/wecom_base_views.xml",
        "views/menu_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "wecom_base/static/src/views/**/*",
        ],
    },
    "license": "AGPL-3",
    "bootstrap": True,
    "post_init_hook": "post_init_hook",
}

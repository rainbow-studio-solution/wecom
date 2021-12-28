# -*- coding: utf-8 -*-
{
    "name": "WeCom API",
    "author": "RStudio",
    "website": "https://gitee.com/rainbowstudio/wecom",
    "sequence": 602,
    "installable": True,
    "application": True,
    "auto_install": False,
    "category": "WeCom/WeCom",
    "version": "14.0.0.1",
    "summary": """
WeCom Service-side API and Client-side API              
        """,
    "description": """
 WeCom Service-side API and Client-side API
 Reconstruction based on project "https://github.com/sbzhu/weworkapi_python"
        """,
    "depends": ["wecom_hrm"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron_data.xml",
        "data/service_api_list_data.xml",
        "data/wecom_server_api_error_data.xml",
        "data/wecom_app_event_type_data.xml",
        "views/assets_templates.xml",
        "views/ir_cron_views.xml",
        # "views/wecom_service_api_views.xml",
        "views/wecom_service_api_list_views.xml",
        "views/wecom_service_api_error_views.xml",
        "views/wecom_apps_views.xml",
        "views/wecom_app_callback_service_views.xml",
        "views/wecom_app_config_views.xml",
        "views/wecom_app_type_views.xml",
        "views/wecom_app_subtype_views.xml",
        "views/wecom_app_event_type_views.xml",
        "views/res_config_settings_views.xml",
        "views/menu.xml",
    ],
    "external_dependencies": {
        "python": ["requests_toolbelt", "pandas", "lxml_to_dict", "pycryptodome"],
    },
    "qweb": ["static/src/xml/*.xml",],
    # "post_init_hook": "post_init_hook",
}

# -*- coding: utf-8 -*-
{
    "name": "WeCom Authentication",
    "author": "RStudio",
    "website": "https://gitee.com/rainbowstudio/wxwork",
    "sequence": 606,
    "installable": True,
    "application": True,
    "auto_install": False,
    "category": "WeCom/WeCom",
    "version": "14.0.0.1",
    "summary": """
        WeCom Authentication
        """,
    "description": """

        """,
    "depends": [
        "auth_oauth",
        "wecom_api",
        "wecom_portal",
        "wecom_message",
    ],
    "data": [
        "data/wecom_oauth_data.xml",
        "data/auth_signup_data.xml",
        "data/ir_cron_data.xml",
        "views/assets_templates.xml",
        "views/res_company_views.xml",
        "views/res_config_settings_views.xml",
        "views/ir_cron_views.xml",
        "views/menu_views.xml",
    ],
    "qweb": [
        "static/src/xml/*.xml",
    ],
}

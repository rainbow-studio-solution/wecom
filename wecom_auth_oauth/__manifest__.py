# -*- coding: utf-8 -*-
{
    "name": "WeCom Authentication",
    "author": "RStudio",
    "website": "https://gitee.com/rainbowstudio/wecom",
    "sequence": 605,
    "installable": True,
    "application": True,
    "auto_install": False,
    "category": "WeCom Suites/Authentication",
    "version": "16.0.0.1",
    "summary": """
        One click login, code scanning login.
        """,
    "description": """

        """,
    "depends": ["portal", "auth_oauth", "wecom_material",],
    "data": [
        "data/wecom_apps_data.xml",
        "data/wecom_app_config_data.xml",
        "data/wecom_oauth_data.xml",
        "views/res_config_settings_views.xml",
        "views/wecom_apps_views.xml",
        "views/auth_signup_login_templates.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "wecom_auth_oauth/static/src/webclient/**/*",
        ],
        "web.assets_frontend": [
            "wecom_auth_oauth/static/src/frontend/**/*",
        ],
    },
    "bootstrap": True,  # 加载登录屏幕的翻译，
    "license": "Other proprietary",
}

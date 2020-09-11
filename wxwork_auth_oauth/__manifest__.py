# -*- coding: utf-8 -*-
{
    "name": "Enterprise WeChat Authentication",
    "author": "RStudio",
    "website": "",
    "sequence": 1,
    "installable": True,
    "application": False,
    "auto_install": False,
    "category": "企业微信",
    "version": "13.0.0.1",
    "summary": """
        Enterprise WeChat Scan code login
        """,
    "description": """

        """,
    "depends": [
        "portal",
        "auth_oauth",
        "wxwork_users_syncing",
    ],
    "data": [
        "data/wxwork_oauth_data.xml",
        "views/wxwork_auth_oauth_templates.xml",
        "views/res_config_settings_views.xml",
        # 'views/auth_oauth_views.xml',
    ],
    "qweb": [
        "static/src/xml/*.xml",
    ],
    "bootstrap": True,  # load translatins for login screen
    "external_dependencies": {
        "python": [],
    },
}

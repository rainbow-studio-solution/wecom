# -*- coding: utf-8 -*-
{
    "name": "Enterprise WeChat Authentication",
    "author": "RStudio",
    "website": "",
    "sequence": 603,
    "installable": True,
    "application": True,
    "auto_install": False,
    "category": "Enterprise WeChat/Enterprise WeChat",
    "version": "14.0.0.1",
    "summary": """
        Enterprise WeChat Authentication
        """,
    "description": """

        """,
    "depends": ["portal", "auth_oauth", "wxwork_users_syncing",],
    "data": [
        "data/wxwork_oauth_data.xml",
        "views/wxwork_auth_oauth_templates.xml",
        "views/res_config_settings_views.xml",
        # 'views/auth_oauth_views.xml',
    ],
    "qweb": ["static/src/xml/*.xml",],
    "external_dependencies": {"python": [],},
}

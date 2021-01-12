# -*- coding: utf-8 -*-
{
    "name": "Enterprise WeChat Authentication",
    "author": "RStudio",
    "website": "https://gitee.com/rainbowstudio/wxwork",
    "sequence": 604,
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
    "depends": [
        # "portal",
        "auth_oauth",
        "wxwork_hr_syncing",
    ],
    "data": [
        "data/wxwork_oauth_data.xml",
        "views/assets_templates.xml",
        "views/res_config_settings_views.xml",
    ],
    "qweb": ["static/src/xml/*.xml",],
}

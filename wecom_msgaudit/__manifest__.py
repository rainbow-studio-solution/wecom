# -*- coding: utf-8 -*-
{
    "name": "WeCom Session Content Archive",
    "author": "RStudio",
    "website": "https://gitee.com/rainbowstudio/wecom",
    "sequence": 630,
    "installable": True,
    "application": True,
    "auto_install": False,
    "category": "WeCom/WeCom",
    "version": "15.0.0.1",
    "summary": """

        """,
    "description": """


        """,
    "depends": ["wecom_contacts"],
    "external_dependencies": {"python": ["pycryptodome", "pandas"],},
    "data": [
        "security/ir.model.access.csv",
        "data/ir_config_parameter.xml",
        "data/wecom_apps_data.xml",
        "data/ir_cron_data.xml",
        "wizard/wecom_modify_external_groupchat_name.xml",
        "wizard/wecom_modify_external_sender_name.xml",
        "views/res_config_settings_views.xml",
        "views/wecom_msgaudit_key_views.xml",
        "views/wecom_chat_data_views.xml",
        "views/ir_cron_views.xml",
        "views/menu_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            # SCSSS
            # JS
            "wecom_msgaudit/static/src/js/list_header_button.js",
        ],
        "web.assets_qweb": ["wecom_msgaudit/static/src/xml/*.xml",],
    },
    "license": "LGPL-3",
}

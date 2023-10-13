# -*- coding: utf-8 -*-
{
    "name": "WeCom Contacts",
    "author": "RStudio",
    "website": "https://gitee.com/rainbowstudio/wecom",
    "sequence": 602,
    "installable": True,
    "application": True,
    "auto_install": False,
    "category": "WeCom Suites/CRM",
    "version": "16.0.0.1",
    "summary": """
        WeCom Contacts
        """,
    "description": """


        """,
    "depends": [
        "contacts",
        "hr",
        "wecom_base",
        "wecom_widget",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron_data.xml",
        "data/wecom_apps_data.xml",
        "views/res_partner_views.xml",
        "views/res_partner_category_views.xml",
        "views/res_users_views.xml",
        "views/res_config_settings_views.xml",
        "views/res_company_views.xml",
        "views/ir_cron_views.xml",
        "views/menu_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "wecom_contacts/static/src/webclient/**/*",
        ],
    },
    "external_dependencies": {
        "python": [],
    },
    "post_init_hook": "post_init_hook",
    "license": "AGPL-3",
    "bootstrap": True,
}

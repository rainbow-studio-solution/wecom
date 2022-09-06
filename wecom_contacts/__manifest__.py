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
    "version": "15.0.0.1",
    "summary": """
        WeCom Contacts
        """,
    "description": """


        """,
    "depends": ["contacts","hr", "wecom_base",],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron_data.xml",
        "data/wecom_apps_data.xml",
        
        "views/res_config_settings_views.xml",
        "views/res_company_views.xml",
        "views/ir_cron_views.xml",
        "views/menu_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            # SCSSS
            # JS
            "wecom_contacts/static/src/js/download_contacts.js",
            "wecom_contacts/static/src/js/download_tags.js",
        ],
        "web.assets_qweb": ["wecom_contacts/static/src/xml/*.xml",],
    },
    "external_dependencies": {"python": [],},
    # "pre_init_hook": "pre_init_hook",
    "license": "LGPL-3",
    "bootstrap": True,
}

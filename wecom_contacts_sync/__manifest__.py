# -*- coding: utf-8 -*-
{
    "name": "WeCom Contacts Synchronized",
    "author": "RStudio",
    "website": "https://gitee.com/rainbowstudio/wecom",
    "sequence": 605,
    "installable": True,
    "application": True,
    "auto_install": False,
    "category": "WeCom/WeCom",
    "version": "15.0.0.1",
    "summary": """
        
        """,
    "description": """


        """,
    "depends": [
        "wecom_contacts",
        "wecom_message",
        "wecom_hrm",
    ],
    "external_dependencies": {
        "python": ["pandas"],
    },
    "data": [
        "security/ir.model.access.csv",
        "data/wecom_app_config_data.xml",
        "data/wecom_app_event_type_data.xml",
        "data/ir_cron_data.xml",
        "views/res_config_settings_views.xml",
        "views/wecom_apps_views.xml",
        "views/ir_cron_views.xml",
        "wizard/wecom_contacts_sync_wizard_views.xml",
        "wizard/wecom_users_sync_wizard_views.xml",
        "views/wecom_contacts_block_views.xml",
        "views/menu_views.xml",
    ],
    "assets": {
        "web._assets_common_styles": [
            "wecom_contacts_sync/static/src/scss/sync_result_dialog.scss",
        ]
    },
    "license": "LGPL-3",
}

# -*- coding: utf-8 -*-
{
    "name": "WeCom Contacts Synchronized",
    "author": "RStudio",
    "website": "https://gitee.com/rainbowstudio/wecom",
    "sequence": 603,
    "installable": True,
    "application": True,
    "auto_install": False,
    "category": "WeCom/WeCom",
    "version": "15.0.0.1",
    "summary": """
        
        """,
    "description": """


        """,
    "depends": ["wecom_contacts", "wecom_hrm",],
    "external_dependencies": {"python": ["pandas"],},
    "data": [
        "security/ir.model.access.csv",
        "data/wecom_app_config_data.xml",
        "data/wecom_app_event_type_data.xml",
        "views/res_config_settings_views.xml",
        "views/wecom_apps_views.xml",
        # "views/wecom_sync_contacys_views.xml",
        "wizard/wecom_contacts_sync_wizard_views.xml",
        "views/menu_views.xml",
    ],
    "license": "LGPL-3",
}

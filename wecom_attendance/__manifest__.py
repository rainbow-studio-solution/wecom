# -*- coding: utf-8 -*-

{
    "name": "WeCom Attendances",
    "author": "RStudio",
    "sequence": 610,
    "installable": True,
    "application": True,
    "auto_install": False,
    "category": "WeCom Suites/Attendances",
    "website": "https://gitee.com/rainbowstudio/wecom",
    "version": "15.0.0.1",
    "summary": """
        
        """,
    "description": """

        """,
    "depends": ["wecom_contacts", "hrms_base", "hrms_attendance",],
    "data": [
        "security/ir.model.access.csv",
        "data/wecom_apps_data.xml",
        "views/res_config_settings_views.xml",
        "views/wecom_checkin_rule_views.xml",
        "wizard/wecom_checkin_rules_wizard_views.xml",
        "views/menu_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            # SCSSS
            "wecom_attendance/static/src/scss/*.scss",
            # JS
            "wecom_attendance/static/src/js/*.js",
            ],
        "web.assets_qweb": ["wecom_attendance/static/src/xml/*.xml",],
    },
    "license": "LGPL-3",
}

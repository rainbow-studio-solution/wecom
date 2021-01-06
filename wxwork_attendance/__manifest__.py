# -*- coding: utf-8 -*-
{
    "name": "Enterprise WeChat Attendances",
    "author": "RStudio",
    "website": "https://gitee.com/rainbowstudio/wxwork",
    "category": "Enterprise WeChat/Enterprise WeChat",
    "version": "14.0.0.1",
    "summary": """

        """,
    "description": """

        """,
    "depends": ["hr_attendance", "wxwork_hr_syncing",],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron_data.xml",
        # "data/wxwork_data.xml",
        # "views/ir_cron_views.xml",
        # "wizard/wizard_wxwork_attendance_data_pull.xml",
        "wizard/wizard_wxwork_attendance_rule_pull.xml",
        "views/assets_templates.xml",
        "views/res_config_settings_views.xml",
        "views/hr_attendance_view.xml",
        "views/hr_attendance_rule_view.xml",
        "views/ir_cron_views.xml",
        "views/menu.xml",
    ],
    "qweb": ["static/src/xml/*.xml",],
    "sequence": 609,
    "installable": True,
    "application": True,
    "auto_install": False,
}

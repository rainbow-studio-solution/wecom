# -*- coding: utf-8 -*-
{
    "name": "企业微信-打卡",
    "author": "RStudio",
    "website": "",
    "sequence": 1,
    "installable": True,
    "application": False,
    "auto_install": False,
    "category": "企业微信",
    "version": "12.0.0.1",
    "summary": """
        获取企业微信打卡数据
        """,
    "description": """
功能：
====================

        """,
    "depends": [
        "hr_attendance",
        "wxwork_users_syncing",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron_data.xml",
        "data/wxwork_data.xml",
        "views/ir_cron_views.xml",
        "wizard/wizard_wxwork_attendance_data_pull.xml",
        "wizard/wizard_wxwork_attendance_rule_pull.xml",
        "views/res_config_settings_views.xml",
        "views/wxwork_attendance_data_views.xml",
        "views/wxwork_attendance_rule_views.xml",
        "views/wxwork_attendance_menu.xml",
    ],
    "qweb": [
        "static/src/xml/*.xml",
    ],
}

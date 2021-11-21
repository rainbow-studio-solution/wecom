# -*- coding: utf-8 -*-
{
    "name": "WeCom Hr Extension",
    "author": "RStudio",
    "website": "https://gitee.com/rainbowstudio/wxwork",
    "sequence": 603,
    "installable": True,
    "application": False,
    "auto_install": False,
    "category": "WeCom/WeCom",
    "version": "14.0.0.1",
    "summary": """
        
        """,
    "description": """


        """,
    "depends": [
        "hr_attendance",
        "hr_contract",
        "hr_expense",
        "hr_gamification",
        "hr_holidays",
        "hr_maintenance",
        "hr_presence",
        "hr_recruitment",
        "hr_recruitment_survey",
        "hr_skills",
        "hr_work_entry",
        "hr_fleet",
        "hr_timesheet_attendance",
    ],
    "data": [
        "views/menu.xml",
    ],
    "qweb": [
        "static/src/xml/*.xml",
    ],
}

# -*- coding: utf-8 -*-
{
    "name": "Enterprise WeChat Hr Extension",
    "author": "RStudio",
    "website": "https://gitee.com/rainbowstudio/wxwork",
    "sequence": 602,
    "installable": True,
    "application": True,
    "auto_install": False,
    "category": "Enterprise WeChat/Enterprise WeChat",
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
        "project_timesheet_holidays",
    ],
    "data": [],
    "qweb": ["static/src/xml/*.xml",],
}

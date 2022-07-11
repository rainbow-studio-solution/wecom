# -*- coding: utf-8 -*-
{
    "name": "Human Resource Management System Extension",
    "author": "RStudio",
    "website": "https://gitee.com/rainbowstudio/wecom",
    "sequence": 609,
    "installable": True,
    "application": True,
    "auto_install": False,
    "category": "WeCom Suites/Human Resources",
    "version": "15.0.0.1",
    "summary": """
        
        """,
    "description": """


        """,
    "depends": [
        "hrms_base",
        "hr_expense",
        "hr_holidays",
        "hr_recruitment",
        "hr_fleet",
        "hr_attendance",
        "hr_skills",
        "hr_contract",
        "hr_work_entry",
        "hr_work_entry_contract",
        "hr_work_entry_holidays",
        "hr_gamification",
        "hr_holidays_attendance",
        "hr_presence",
        "hr_recruitment_survey",
        "project_timesheet_holidays",
        "hr_maintenance",
        "gamification",
    ],
    "data": ["views/menu_views.xml",],
    "external_dependencies": {"python": [],},
    "license": "LGPL-3",
}

# -*- coding: utf-8 -*-
{
    "name": "HRMS Expenses",
    "author": "RStudio",
    "website": "https://gitee.com/rainbowstudio/wecom",
    "sequence": 505,
    "installable": True,
    "application": False,
    "auto_install": False,
    "category": "WeCom Suites/Human Resources",
    "version": "15.0.0.1",
    "summary": """
        
        """,
    "description": """


        """,
    "depends": ["hrms_base", "hr_expense",],
    "data": ["views/menu_views.xml", "views/res_config_settings_views.xml"],
    "assets": {"web.assets_qweb": ["hrms_expense/static/src/xml/*.xml",],},
    "external_dependencies": {"python": [],},
    "license": "LGPL-3",
}

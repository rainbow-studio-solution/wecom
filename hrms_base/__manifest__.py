# -*- coding: utf-8 -*-

{
    "name": "HRMS",
    "author": "RStudio",
    "sequence": 501,
    "installable": True,
    "application": True,
    "auto_install": False,
    "category": "WeCom Suites/Human Resources",
    "website": "https://gitee.com/rainbowstudio/wecom",
    "version": "15.0.0.1",
    "summary": """
        
        """,
    "description": """

        """,
    "depends": ["hr","hr_contract","hr_skills", "web_multi_level_menu",],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_config_parameter.xml",
        # "data/hr_data.xml",
        "wizard/hr_plan_wizard_views.xml",
        "wizard/employee_bind_wecom_views.xml",
        "wizard/user_bind_wecom_views.xml",
        "views/ir_ui_menu_views.xml",
        "views/res_config_settings_views.xml",
        "views/hr_department_view.xml",
        "views/hr_employee_view.xml",
        "views/hr_employee_category_views.xml",
        "views/menu_views.xml",
    ],
    "assets": {
        
    },
    "external_dependencies": {"python": [],},
    "license": "LGPL-3",
}

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
    "summary": "Human Resource Management System",
    "description": """

        """,
    "depends": ["hr", "hr_work_entry_contract", "hr_skills", "web_multi_level_menu",],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_config_parameter.xml",
        # "data/hr_data.xml",
        "wizard/hr_plan_wizard_views.xml",
        "wizard/hr_menu_wizard_views.xml",
        # "views/ir_ui_menu_views.xml",
        "views/res_config_settings_views.xml",
        "views/hr_department_view.xml",
        "views/hr_employee_view.xml",
        "views/hr_employee_category_views.xml",
        "views/menu_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            # SCSSS
            "hrms_base/static/src/scss/hrms_settings_navigation.scss",
            # JS
            "hrms_base/static/src/js/hrms_settings_navigation.js",
        ],
        "web.assets_qweb": ["hrms_base/static/src/xml/*.xml",],
    },
    "external_dependencies": {"python": [],},
    "license": "LGPL-3",
    "bootstrap": True,
}

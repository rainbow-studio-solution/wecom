# -*- coding: utf-8 -*-

{
    "name": "WeCom HRM",
    "author": "RStudio",
    "sequence": 602,
    "installable": True,
    "application": True,
    "auto_install": False,
    "category": "WeCom/WeCom",
    "website": "https://gitee.com/rainbowstudio/wxwork",
    "version": "14.0.0.1",
    "summary": """
        
        """,
    "description": """

        """,
    "depends": ["hr", "wecom_api",],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_config_parameter.xml",
        "data/hr_data.xml",
        # "views/res_company_views.xml",
        # "views/res_config_settings_views.xml",
        # "views/res_users_views.xml",
        "views/hr_department_view.xml",
        "views/hr_employee_category_views.xml",
        "views/hr_employee_view.xml",
        "views/wecom_contacts_block_views.xml",
        "views/ir_ui_menu_views.xml",
        "views/menu.xml",
    ],
    "qweb": ["static/src/xml/*.xml",],
    "external_dependencies": {"python": [],},
}

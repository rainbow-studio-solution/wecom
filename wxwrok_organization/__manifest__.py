# -*- coding: utf-8 -*-
{
    "name": "Enterprise WeChat Organization",
    "summary": """
        Enterprise WeChat Organization""",
    "description": """
         Enterprise WeChat Organization
    """,
    "author": "RStudio",
    "website": "https://gitee.com/rainbowstudio/wxwork",
    "category": "Enterprise WeChat/Enterprise WeChat",
    "version": "14.0.0.1",
    # any module necessary for this one to work correctly
    "depends": ["hr", "wxwork_base"],
    "data": [
        # 'security/ir.model.access.csv',
        "data/hr_data.xml",
        "data/ir_config_parameter.xml",
        "views/hr_department_view.xml",
        "views/hr_employee_view.xml",
        "views/res_users_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "sequence": 602,
    "installable": True,
    "application": True,
    "auto_install": False,
}

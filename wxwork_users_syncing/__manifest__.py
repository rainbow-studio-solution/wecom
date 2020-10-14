# -*- coding: utf-8 -*-
{
    "name": "Enterprise WeChat User Syncing",
    "author": "RStudio",
    "website": "",
    "sequence": 602,
    "installable": True,
    "application": True,
    "auto_install": False,
    "category": "Enterprise WeChat/Enterprise WeChat",
    "version": "14.0.0.1",
    "summary": """
        Enterprise WeChat users are synchronized to Odoo Hr and Users
        """,
    "description": """


        """,
    "depends": [
        "base",
        "mail",
        "hr",
        "auth_oauth",
        "wxwork_api",
        # "wxwork_message_push",
    ],
    "external_dependencies": {"python": ["numpy", "opencv-python",],},
    "data": [
        # "data/ir_cron_data.xml",
        # "data/ir_config_parameter.xml",
        # "views/ir_cron_views.xml",
        # "views/hr_department_view.xml",
        # "views/hr_employee_view.xml",
        # "views/res_users_views.xml",
        # "views/wxwork_contacts_views.xml",
        # "views/res_config_settings_views.xml",
    ],
    "qweb": ["static/src/xml/*.xml",],
}

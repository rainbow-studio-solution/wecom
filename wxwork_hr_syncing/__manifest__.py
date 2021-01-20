# -*- coding: utf-8 -*-
{
    "name": "Enterprise WeChat Hr Syncing",
    "author": "RStudio",
    "website": "https://gitee.com/rainbowstudio/wxwork",
    "sequence": 603,
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
    "depends": ["base", "mail", "auth_oauth", "wxwork_api", "wxwork_hr",],
    "external_dependencies": {"python": ["numpy", "opencv-python",],},
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron_data.xml",
        "data/auth_oauth_data.xml",
        "views/ir_cron_views.xml",
        "views/hr_employee_view.xml",
        "views/res_users_views.xml",
        "views/res_config_settings_views.xml",
        "wizard/wizard_wxwork_contacts_sync.xml",
        "wizard/wizard_wxwork_sync_user.xml",
        "wizard/wizard_wxwork_sync_tag.xml",
        "views/assets_templates.xml",
        "views/menu_views.xml",
    ],
    "qweb": ["static/src/xml/*.xml",],
}

# -*- coding: utf-8 -*-
{
    "name": "企业微信-通知",
    "author": "RStudio",
    "website": "",
    "sequence": 1,
    "installable": True,
    "application": True,
    "auto_install": False,
    "category": "企业微信",
    "version": "12.0.0.1",
    "summary": """
        Odoo事件通知到企业微信
        """,
    "description": """
功能：
====================

        """,
    "depends": [
        "mail",
        "wxwork_users_syncing",
    ],
    "data": [
        # 'data/wxwork_data.xml',
        "views/wxwork_notice_template_views.xml",
        "views/res_config_settings_views.xml",
        "security/ir.model.access.csv",
    ],
    "qweb": [
        "static/src/xml/*.xml",
    ],
    "bootstrap": True,  # load translations for login screen
    # 'external_dependencies': {'python': ['skimage']},
}

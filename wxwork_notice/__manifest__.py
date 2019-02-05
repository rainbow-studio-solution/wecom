# -*- coding: utf-8 -*-
{
    'name': "企业微信-通知",
    'author': "RStudio",
    'website': "",
    'sequence': 1,
    'installable': True,
    'application': True,
    'auto_install': False,
    'category': '企业微信',
    'version': '12.0.0.1',
    'summary': """
        Odoo事件通知到企业微信
        """,
    'description': """
功能：
====================

        """,
    'depends': [
        'wxwork_contacts',
    ],
    'data': [
        # 'data/wxwork_data.xml',
        # 'views/reset_password_templates.xml',
        # 'views/reset_password_views.xml',
    ],
    'qweb': [
        "static/src/xml/*.xml",
    ],
    'bootstrap': True,  # load translations for login screen
    # 'external_dependencies': {'python': ['skimage']},

}

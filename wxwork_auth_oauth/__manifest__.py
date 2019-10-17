# -*- coding: utf-8 -*-
{
    'name': "企业微信-登录授权",
    'author': "RStudio",
    'website': "",
    'sequence': 1,
    'installable': True,
    'application': True,
    'auto_install': False,
    'category': '企业微信',
    'version': '13.0.0.1',
    'summary': """
        企业微信OAuth的授权登录和扫码登录
        """,
    'description': """
功能：
====================

        """,
    'depends': [
        'portal',
        'auth_oauth',
        'wxwork_contacts',
    ],
    'data': [
        'data/wxwork_oauth_data.xml',
        'views/wxwork_auth_oauth_templates.xml',
        'views/res_config_settings_views.xml',
        # 'views/auth_oauth_views.xml',
    ],
    'qweb': [
        "static/src/xml/*.xml",
    ],
    'bootstrap': True,  # load translatins for login screen
    'external_dependencies': {
        'python': [

        ],
    },
}

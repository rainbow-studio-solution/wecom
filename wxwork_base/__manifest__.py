# -*- coding: utf-8 -*-
{
    'name': "企业微信",
    'author': "RStudio",
    'website': "",
    'sequence': 1,
    'installable': True,
    'application': True,
    'auto_install': False,
    'category': '企业微信',
    'version': '12.0.0.1',
    'summary': """
        企业微信基础模块
        """,
    'description': """
功能：
====================
企业微信用户同步，企业微信一键登录
        """,
    'depends': [
        # 'wxwork_contacts',
    ],
    'data': [
        'data/wxwork_data.xml',
        'views/res_config_settings_views.xml',
        'views/wxwork_base_views.xml',
    ],
    'qweb': [
        "static/src/xml/*.xml",
    ],
    'bootstrap': True,  # load translations for login screen
    'external_dependencies': {
        'python': [

        ],
    },
}

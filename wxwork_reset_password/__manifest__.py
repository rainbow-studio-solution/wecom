# -*- coding: utf-8 -*-
{
    'name': "企业微信-密码重置",
    'author': "RStudio",
    'website': "",
    'sequence': 1,
    'installable': True,
    'application': True,
    'auto_install': False,
    'category': '企业微信',
    'version': '12.0.0.1',
    'summary': """
        登录页面和后台用户使用企业微信扫码验证更改密码
        """,
    'description': """
功能：
====================

        """,
    'depends': [
        'auth_signup',
        'wxwork_auth_oauth',
    ],
    'data': [
        # 'data/ir_cron_data.xml',
        # 'views/ir_cron_views.xml',
    ],
    'qweb': [
        "static/src/xml/*.xml",
    ],
    'bootstrap': True,  # load translations for login screen
    # 'external_dependencies': {'python': ['skimage']},

}

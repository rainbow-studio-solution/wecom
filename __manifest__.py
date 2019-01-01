# -*- coding: utf-8 -*-
{
    'name': u"企业微信",
    'author': "RStudio",
    'website': "",
    'sequence': 1,
    'installable': True,
    'application': True,
    'auto_install': False,
    'category': 'Social Network',
    'version': '12.0.0.1',
    'summary': """
        企业微信用户同步，企业微信一键登录，消息通知
        """,
    'description': """
    功能：
    -----------------------
    企业微信用户同步，企业微信一键登录
        """,
    'depends': [
        'base',
        'auth_oauth',
        'hr',
    ],
    'data': [
        'data/wxwork_data.xml',
        'data/ir_cron_data.xml',
        'wizard/wizard_wxwork_contacts_sync.xml',
        'views/res_config_settings_views.xml',
        'views/hr_department_view.xml',
        'views/hr_employee_view.xml',
        'views/wxwork_views.xml',
        'views/wxwork_templates.xml',
    ],
    'qweb': [
        "static/src/xml/*.xml",
    ],
    'bootstrap': True,  # load translations for login screen
    'live_test_url': 'http://58.49.117.179:8069',
    'images': ['images/main_screenshot.png'],
    'currency': 'EUR',
    'price': 109,
    'external_dependencies': {
        'python': [

        ],
    },
}

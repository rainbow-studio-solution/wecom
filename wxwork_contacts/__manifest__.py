# -*- coding: utf-8 -*-
{
    'name': "企业微信-通讯簿同步",
    'author': "RStudio",
    'website': "",
    'sequence': 1,
    'installable': True,
    'application': True,
    'auto_install': False,
    'category': '企业微信',
    'version': '12.0.0.1',
    'summary': """
        企业微信通讯簿生成HR及USER
        """,
    'description': """
功能：
====================

        """,
    'depends': [
        'base',
        'hr',
        'portal',
        'wxwork_base',
    ],
    'data': [
        'data/ir_cron_data.xml',
        'views/ir_cron_views.xml',
        'data/wxwork_data.xml',
        'wizard/wizard_wxwork_contacts_sync.xml',
        'views/hr_department_view.xml',
        'views/hr_employee_view.xml',
        'views/res_users_views.xml',
        'views/wxwork_contacts_views.xml',
        'views/res_config_settings_views.xml',
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

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
    'version': '13.0.0.1',
    'summary': """
        同步企业微信通讯簿到HR
        """,
    'description': """
功能：
====================

        """,
    'depends': [
        'base',
        'mail',
        'hr',
        'auth_oauth',
        'wxwork_base',
    ],
    'data': [
        'data/ir_cron_data.xml',
        'data/wxwork_data.xml',
        'views/ir_cron_views.xml',
        'wizard/wizard_wxwork_contacts_sync.xml',
        'wizard/wizard_wxwork_sync_user.xml',
        'views/hr_department_view.xml',
        'views/hr_employee_view.xml',
        'views/res_users_views.xml',
        'views/wxwork_contacts_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'qweb': [
        "static/src/xml/*.xml",
    ],
}

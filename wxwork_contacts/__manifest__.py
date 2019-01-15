# -*- coding: utf-8 -*-
{
    'name': "企业微信-通讯簿同步",
    'author': "RStudio",
    'website': "",
    'sequence': 1,
    'installable': True,
    # 'application': True,
    'auto_install': False,
    'category': '企业微信',
    'version': '12.0.0.1',
    'summary': """
        企业微信用户同步生成HR及USER
        """,
    'description': """
功能：
====================

        """,
    'depends': [
        'base',
        'hr',
        'portal',
        'eis_auth_oauth',
    ],
    'data': [
        'data/wxwork_data.xml',
        'data/ir_cron_data.xml',
        'wizard/wizard_wxwork_contacts_sync.xml',
        'views/res_config_settings_views.xml',
        'views/hr_department_view.xml',
        'views/hr_employee_view.xml',
        'views/res_users_views.xml',
        'views/wxwork_views.xml',
        'views/wxwork_templates.xml',
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

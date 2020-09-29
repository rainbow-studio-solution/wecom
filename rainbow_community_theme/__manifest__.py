# -*- coding: utf-8 -*-

{
    'name':
    'Rainbow Community Theme',
    'category':
    "Themes/Backend",
    'version':
    '13.0.0.1',
    'author':
    "RStudio",
    'description':
    """
Rainbow Community Theme
===========================

Backend/Launcher/Multi-level menu/Theme Settings/Custom login page/
        """,
    'depends': [
        'base_setup',
        'web',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_config_parameter.xml',
        'views/assets_templates.xml',
        'views/layout_templates.xml',
        'views/res_config_settings_views.xml',
        'views/rainbow_menu.xml',
        'views/login_templates.xml',
        'views/login_form_templates.xml',
        'views/signup_templates.xml',
        'views/signup_reset_password_templates.xml',
        'views/auth_oauth_templates.xml',
        'views/mail_assets_templates.xml',
    ],
    'qweb': [
        "static/src/xml/*.xml",
    ],
    'live_test_url':
    'https://rainbow.rstudio.xyz/',
    'license':
    'AGPL-3',
    'auto_install':
    False,
    'application':
    False,
    'installable':
    True,
    'images': ['images/main_screenshot.png'],
    'images': ['images/rainbow.png', 'images/rainbow_screenshot.png'],

}

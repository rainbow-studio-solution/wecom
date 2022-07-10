# -*- coding: utf-8 -*-
{
    "name": "WeCom Message",
    "author": "RStudio",
    "website": "https://gitee.com/rainbowstudio/wecom",
    "sequence": 606,
    "installable": True,
    "application": True,
    "auto_install": False,
    "category": "WeCom Suites/Messages",
    "version": "15.0.0.1",
    "summary": """
        Odoo event notification to WeCom
        """,
    "description": """


        """,
    "depends": [
        "mail",
        "digest",
        "rating",
        "wecom_material",
    ],
    "external_dependencies": {"python": ["html2text", "lxml"],},
    "data": [
        "security/wecom_message_security.xml",
        "security/ir.model.access.csv",
        "data/ir_config_parameter.xml",
        "data/wecom_apps_data.xml",
        "data/auth_signup_message_template_data.xml",
        "data/auth_totp_message_template_data.xml",
        "data/portal_message_template_data.xml",
        "data/followers_message_template_data.xml",
        "wizard/mail_template_preview_views.xml",
        "wizard/invite_view.xml",
        # "views/assets_templates.xml",
        "views/res_users_views.xml",
        "views/res_config_settings_views.xml",
        "views/res_company_views.xml",
        "views/mail_message_views.xml",
        "views/mail_template_views.xml",
        "views/mail_mail_views.xml",
        "views/mail_notification_views.xml",
        "views/menu_views.xml",
    ],
    "assets": {"web.assets_backend": [],},
    # "post_init_hook": "_auto_install_lang",
    # 'external_dependencies': {'python': ['skimage']},
    "license": "LGPL-3",
}

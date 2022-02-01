# -*- coding: utf-8 -*-
{
    "name": "WeCom Message",
    "author": "RStudio",
    "website": "https://gitee.com/rainbowstudio/wecom",
    "sequence": 605,
    "installable": True,
    "application": True,
    "auto_install": False,
    "category": "WeCom/WeCom",
    "version": "14.0.0.1",
    "summary": """
        Odoo event notification to WeCom
        """,
    "description": """


        """,
    "depends": [
        "mail",
        # "digest",
        "rating",
        "wecom_widget",
        "wecom_material",
        "wecom_auth_oauth",
    ],
    "external_dependencies": {"python": ["html2text", "lxml"],},
    "data": [
        "security/ir.model.access.csv",
        "data/wecom_apps_data.xml",
        "data/auth_signup_data.xml",
        # "data/message_template_data.xml",
        "wizard/mail_template_preview_views.xml",
        "views/assets_templates.xml",
        # "views/mail_message_views.xml",
        "views/res_users_views.xml",
        "views/res_config_settings_views.xml",
        "views/mail_template_views.xml",
        "views/mail_mail_views.xml",
        # "views/wecom_message_message_views.xml",
        # "views/wecom_apps_views.xml",
        # "views/wecom_message_notification_views.xml",
        "views/menu.xml",
    ],
    "qweb": ["static/src/xml/*.xml",],
    # "post_init_hook": "_auto_install_lang",
    # 'external_dependencies': {'python': ['skimage']},
}

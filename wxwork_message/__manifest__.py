# -*- coding: utf-8 -*-
{
    "name": "Enterprise WeChat Message",
    "author": "RStudio",
    "website": "https://gitee.com/rainbowstudio/wxwork",
    "sequence": 607,
    "installable": True,
    "application": False,
    "auto_install": False,
    "category": "Enterprise WeChat/Enterprise WeChat",
    "version": "14.0.0.1",
    "summary": """
        Odoo event notification to enterprise WeChat
        """,
    "description": """


        """,
    "depends": [
        "mail",
        "wxwork_base",
        "wxwork_widget",
        "wxwork_material",
        "wxwork_hr_syncing",
    ],
    "external_dependencies": {"python": ["html2text"],},
    "data": [
        "security/ir.model.access.csv",
        # "data/wxwork_message_data.xml",
        "wizard/wxwork_message_template_preview_views.xml",
        "views/assets_templates.xml",
        "views/wxwork_message_views.xml",
        "views/res_config_settings_views.xml",
        # "views/wxwork_mail_views.xml",
        "views/wxwork_message_template_views.xml",
        "views/menu.xml",
    ],
    "qweb": ["static/src/xml/*.xml",],
    # "post_init_hook": "_auto_install_lang",
    # 'external_dependencies': {'python': ['skimage']},
}

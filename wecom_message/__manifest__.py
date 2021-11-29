# -*- coding: utf-8 -*-
{
    "name": "WeCom Message",
    "author": "RStudio",
    "website": "https://gitee.com/rainbowstudio/wxwork",
    "sequence": 604,
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
        "wecom_base",
        "wecom_widget",
        "wecom_material",
    ],
    "external_dependencies": {
        "python": ["html2text", "lxml"],
    },
    "data": [
        "security/ir.model.access.csv",
        "data/res_company_data.xml",
        "data/partner_message_data.xml",
        # "wizard/mail_template_preview_views.xml",
        "views/assets_templates.xml",
        # "views/mail_message_views.xml",
        "views/res_company_views.xml",
        "views/res_config_settings_views.xml",
        "views/wecom_message_template_views.xml",
        "views/wecom_message_message_views.xml",
        "views/menu.xml",
    ],
    "qweb": [
        "static/src/xml/*.xml",
    ],
    # "post_init_hook": "_auto_install_lang",
    # 'external_dependencies': {'python': ['skimage']},
}

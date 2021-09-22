# -*- coding: utf-8 -*-

{
    "name": "Chinese website Extension",
    "author": "RStudio",
    "website": "",
    "category": "Website/Website",
    "version": "14.0.0.1",
    "summary": "Baidu map,Baidu Analytics,social media,ICP filing",
    "description": """

========================
        """,
    "depends": ["website", "web_widget_colorpicker"],
    "data": [
        "data/res_company_data.xml",
        "views/res_config_settings_views.xml",
        "views/res_company_views.xml",
        "views/website_views.xml",
        "views/assets_templates.xml",
        "views/website_templates.xml",
        "views/social_media.xml",
    ],
    "qweb": ["static/src/xml/*.xml",],
    "auto_install": False,
    "application": True,
    "installable": True,
}

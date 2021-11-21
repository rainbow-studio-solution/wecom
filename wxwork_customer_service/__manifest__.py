# -*- coding: utf-8 -*-
{
    "name": "WeCom Customer Service",
    "author": "RStudio",
    "website": "https://gitee.com/rainbowstudio/wxwork",
    "sequence": 610,
    "installable": True,
    "application": True,
    "auto_install": False,
    "category": "WeCom/WeCom",
    "version": "14.0.0.1",
    "summary": """
        """,
    "description": """


        """,
    "depends": ["wecom_base", "wecom_hr"],
    "external_dependencies": {
        "python": [],
    },
    "data": [
        "views/res_company_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "qweb": [
        "static/src/xml/*.xml",
    ],
}

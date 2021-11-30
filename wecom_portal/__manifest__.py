# -*- coding: utf-8 -*-
{
    "name": "WeCom Employee Portal",
    "author": "RStudio",
    "website": "https://gitee.com/rainbowstudio/wxwork",
    "sequence": 605,
    "installable": True,
    "application": True,
    "auto_install": False,
    "category": "WeCom/WeCom",
    "version": "14.0.0.1",
    "summary": """
        WeCom Employee Portal
        """,
    "description": """


        """,
    "depends": [
        "wecom_base",
        "portal",
    ],
    "external_dependencies": {
        "python": [],
    },
    "data": [
        "data/wecom_portal_data.xml",
        "views/portal_templates.xml",
    ],
    "qweb": [
        "static/src/xml/*.xml",
    ],
}

# -*- coding: utf-8 -*-
{
    "name": "Wecom Mass Messagling",
    "summary": "Design, send and track Wecom Message",
    "author": "RStudio",
    "website": "https://gitee.com/rainbowstudio/wxwork",
    "sequence": 607,
    "installable": True,
    "application": False,
    "auto_install": False,
    "category": "WeCom/WeCom",
    "version": "14.0.0.1",
    "description": """


        """,
    "depends": ["portal", "wecom_message"],
    "external_dependencies": {},
    "data": [
        "security/wecom_mass_messaging_security.xml",
        "security/ir.model.access.csv",
        "views/menu.xml",
        "views/wecom_mass_message_views.xml",
    ],
    "qweb": [
        "static/src/xml/*.xml",
    ],
}

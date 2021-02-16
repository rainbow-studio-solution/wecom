# -*- coding: utf-8 -*-
{
    "name": "Enterprise WeChat Material",
    "author": "RStudio",
    "website": "https://gitee.com/rainbowstudio/wxwork",
    "sequence": 610,
    "installable": True,
    "application": True,
    "auto_install": False,
    "category": "Enterprise WeChat/Enterprise WeChat",
    "version": "14.0.0.1",
    "summary": """
        Enterprise WeChat material management 
        """,
    "description": """


        """,
    "depends": ["attachment_indexation", "wxwork_base"],
    "data": [
        "security/ir.model.access.csv",
        "data/material_data.xml",
        "views/material_views.xml",
        "views/menu.xml",
    ],
    "qweb": ["static/src/xml/*.xml",],
}

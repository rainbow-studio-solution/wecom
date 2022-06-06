# -*- coding: utf-8 -*-

{
    "name": "WeCom wedrive",
    "author": "RStudio",
    "category": "WeCom/WeCom",
    "summary": "Enterprises can operate and set permissions for files on the microdisk through the microdisk related interfaces.",
    "website": "https://gitee.com/rainbowstudio/wecom",
    "version": "15.0.0.1",
    "description": """ 

""",
    "depends": [
        "wecom_hrm",
    ],
    "data": [
        # "views/assets_templates.xml",
    ],
    "assets": {
        "web.assets_backend": [
            # SCSSS
    
            # js
  
        ],
        "web.assets_qweb": [
            "wecom_widget/static/src/xml/*.xml",
        ],
    },
    "sequence": 608,
    "installable": True,
    "auto_install": False,
    "application": True,
    "license": "LGPL-3",
}

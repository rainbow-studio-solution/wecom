# -*- coding: utf-8 -*-
{
    "name": "Wecom KPI Digests Message",
    "author": "RStudio",
    "website": "https://gitee.com/rainbowstudio/wecom",
    "sequence": 606,
    "installable": True,
    "application": False,
    "auto_install": False,
    "category": "WeCom Suites/Messages",
    "version": "15.0.0.1",
    "summary": """
Use Enterprise WeChat to periodically send KPI digest messages periodically.  
""",
    "description": """
Use Enterprise WeChat to periodically send KPI digest messages periodically.
""",
    "depends": ["digest", "wecom_message",],
    "data": [
        "data/digest_data.xml", 
        "views/digest_views.xml", 
        "views/res_config_settings_views.xml",
        "views/menu_views.xml",
    ],
    "assets": {"web.assets_backend": [],},
    "license": "LGPL-3",
}
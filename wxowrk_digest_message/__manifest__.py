# -*- coding: utf-8 -*-
{
    "name": "WeCom KPI Digests Message",
    "author": "RStudio",
    "website": "https://gitee.com/rainbowstudio/wxwork",
    "sequence": 614,
    "installable": True,
    "application": False,
    "auto_install": False,
    "category": "WeCom/WeCom",
    "version": "14.0.0.1",
    "summary": """
Use WeCom to periodically send KPI digest messages periodically.  
""",
    "description": """
Use WeCom to periodically send KPI digest messages periodically.
""",
    "depends": [
        "digest",
        "wecom_message",
    ],
    "data": [
        "data/digest_data.xml",
        "views/digest_views.xml",
    ],
    "qweb": [
        "static/src/xml/*.xml",
    ],
}

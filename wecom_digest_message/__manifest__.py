# -*- coding: utf-8 -*-
{
    "name": "Wecom KPI Digests Message",
    "author": "RStudio",
    "website": "https://gitee.com/rainbowstudio/wecom",
    "sequence": 614,
    "installable": True,
    "application": False,
    "auto_install": False,
    "category": "WeCom/WeCom",
    "version": "14.0.0.1",
    "summary": """
Use Enterprise WeChat to periodically send KPI digest messages periodically.  
""",
    "description": """
Use Enterprise WeChat to periodically send KPI digest messages periodically.
""",
    "depends": ["digest", "wecom_material", "wecom_message",],
    "data": ["data/digest_data.xml", "views/digest_views.xml",],
    "qweb": ["static/src/xml/*.xml",],
}

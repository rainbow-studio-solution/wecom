# -*- coding: utf-8 -*-
{
    "name": "Enterprise WeChat KPI Digests Message",
    "author": "RStudio",
    "website": "https://gitee.com/rainbowstudio/wxwork",
    "sequence": 614,
    "installable": True,
    "application": False,
    "auto_install": False,
    "category": "Enterprise WeChat/Enterprise WeChat",
    "version": "14.0.0.1",
    "summary": """
Use Enterprise WeChat to periodically send KPI digest messages periodically.  
""",
    "description": """
Use Enterprise WeChat to periodically send KPI digest messages periodically.
""",
    "depends": ["digest", "wxwork_message",],
    "data": ["data/digest_data.xml", "views/digest_views.xml",],
    "qweb": ["static/src/xml/*.xml",],
}

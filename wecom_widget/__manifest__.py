# -*- coding: utf-8 -*-

{
    "name": "WeCom Widget",
    "author": "RStudio",
    "category": "WeCom Suites/Widget",
    "summary": "WeCom Widget",
    "website": "https://gitee.com/rainbowstudio/wecom",
    "version": "16.0.0.1",
    "description": """

""",
    "depends": [
        "web",
    ],
    "data": [],
    "assets": {
        "web.assets_common": [],
        "web.assets_backend": [
            "wecom_widget/static/src/webclient/**/*",
            # "wecom_widget/static/src/views/**/*",
            "wecom_widget/static/src/components/**/*",
        ],
    },
    "sequence": 600,
    "installable": True,
    "auto_install": True,
    "application": False,
    "license": "AGPL-3",
}

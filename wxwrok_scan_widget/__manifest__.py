# -*- coding: utf-8 -*-
{
    "name": "Enterprise WeChat Scan Code Widget",
    "author": "RStudio",
    "website": "",
    "sequence": 1,
    "installable": True,
    "application": True,
    "auto_install": False,
    "category": "wxwork",
    "version": "13.0.0.1",
    "summary": """
        Enterprise WeChat Scan Code,Support QR code and barcode.
        """,
    "description": """


        """,
    "depends": [
        "stock",
        "wxwork_base",
        "wxwork_users_syncing",
    ],
    "external_dependencies": {
        "python": [],
    },
    "data": [
        "views/assets_templates.xml",
    ],
    "qweb": [
        "static/src/xml/*.xml",
    ],
}

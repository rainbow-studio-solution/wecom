# -*- coding: utf-8 -*-

{
    "name": "iERP Web Widgets",
    "author": "RStudio",
    "category": "iERP Suites/Widget",
    "summary": "iERP Widgets",
    "website": "https://eis-solution.coding.net/public/odoo/oec/git",
    "version": "16.0.0.1",
    "description": """

""",
    "depends": [
        "web",
    ],
    "external_dependencies": {
        "python": [
            "pyzbar",
        ],
    },
    "data": [],
    "assets": {
        "web.assets_common": [
            "web_widgets/static/fonts/fonts.scss",
        ],
        "web.assets_backend": [
            "web_widgets/static/src/views/**/*",
            "web_widgets/static/src/webclient/**/*",
        ],
        "web.assets_frontend": [
            # "web_widgets/static/lib/officetohtml/**/*",
        ],
    },
    "sequence": 500,
    "installable": True,
    "auto_install": True,
    "application": False,
    "license": "AGPL-3",
}

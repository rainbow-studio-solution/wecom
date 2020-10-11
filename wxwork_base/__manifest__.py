# -*- coding: utf-8 -*-

{
    "name": "Enterprise WeChat Base",
    "author": "RStudio",
    "sequence": 1,
    "installable": True,
    "application": True,
    "auto_install": False,
    "category": "Enterprise WeChat",
    "version": "14.0.0.1",
    "summary": """
        Enterprise WeChat Base
        """,
    "description": """

        """,
    "depends": [
        # "web_advanced_dialog"
    ],
    "data": [
        "data/ir_config_parameter.xml",
        "views/res_config_settings_views.xml",
        "views/wxwork_base_views.xml",
    ],
    "qweb": [
        "static/src/xml/*.xml",
    ],
    "external_dependencies": {
        "python": [],
    },
}

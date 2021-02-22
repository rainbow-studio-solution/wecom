# -*- coding: utf-8 -*-

{
    "name": "Enterprise WeChat Base",
    "author": "RStudio",
    "sequence": 600,
    "installable": True,
    "application": False,
    "auto_install": False,
    "category": "Enterprise WeChat/Enterprise WeChat",
    "website": "https://gitee.com/rainbowstudio/wxwork",
    "version": "14.0.0.1",
    "summary": """
        
        """,
    "description": """

        """,
    "depends": ["wxwork_l10n", "wxwork_api"],
    "data": [
        "security/wxwork_security.xml",
        "data/ir_module_category_data.xml",
        "views/res_company_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "qweb": ["static/src/xml/*.xml",],
    "external_dependencies": {"python": [],},
}

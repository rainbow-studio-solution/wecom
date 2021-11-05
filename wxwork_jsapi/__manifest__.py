# -*- coding: utf-8 -*-
{
    "name": "Enterprise WeChat JSAPI",
    "author": "RStudio",
    "website": "",
    "sequence": 600,
    "installable": True,
    "application": False,
    "auto_install": False,
    "category": "Enterprise WeChat/Enterprise WeChat",
    "version": "14.0.0.1",
    "summary": """
        
        """,
    "description": """


        """,
    "depends": ["wxwork_base",],
    "external_dependencies": {"python": [],},
    "data": [
        "data/res_company_data.xml",
        # "data/ir_config_parameter.xml",
        "views/res_company_views.xml",
        # "views/res_config_settings_views.xml",
        # "views/ir_cron_views.xml",
        # "views/menu.xml",
        # "views/assets_templates.xml",
    ],
    "qweb": ["static/src/xml/*.xml",],
}

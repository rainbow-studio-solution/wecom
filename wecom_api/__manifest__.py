# -*- coding: utf-8 -*-
{
    "name": "WeCom API",
    "author": "RStudio",
    "website": "https://gitee.com/rainbowstudio/wecom",
    "sequence": 600,
    "installable": True,
    "application": False,
    "auto_install": False,
    "category": "WeCom Suites/Settings",
    "version": "16.0.0.1",
    "summary": """
WeCom Service-side API and Client-side API
        """,
    "description": """
 WeCom Service-side API and Client-side API
 Reconstruction based on project "https://github.com/sbzhu/weworkapi_python"
        """,
    "depends": [],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_config_parameter.xml",
        "data/wecom_server_api_error_data.xml",
        "data/service_api_list_data.xml",
        "views/assets_templates.xml",
    ],
    "assets": {
        "web.assets_common": [
            # JS
            # "wecom_api/static/src/js/*.js",
        ],
        "web.assets_backend": [
            # JS
        ],
    },
    "external_dependencies": {
        "python": [
            "requests_toolbelt",
            "pandas",
            "xmltodict",
            "pycryptodome",
            "html2text",
        ],
    },
    "license": "AGPL-3",
    # "post_init_hook": "post_init_hook",
}

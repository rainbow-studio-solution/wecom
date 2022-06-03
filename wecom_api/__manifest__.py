# -*- coding: utf-8 -*-
{
    "name": "WeCom API",
    "author": "RStudio",
    "website": "https://gitee.com/rainbowstudio/wecom",
    "sequence": 600,
    "installable": True,
    "application": False,
    "auto_install": False,
    "category": "WeCom/WeCom",
    "version": "15.0.0.1",
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
        "data/wecom_server_api_error_data.xml",
        "data/service_api_list_data.xml",
        "views/ir_cron_views.xml",
    ],
    "assets": {
        "web.assets_common": [
            # JS
            "https://res.wx.qq.com/open/js/jweixin-1.2.0.js",
            "wecom_api/static/src/js/wxconfig.js",
        ],
        "web.assets_backend": [
            # JS
            
        ],
        "web.assets_qweb": ["wecom_api/static/src/xml/*.xml",],
    },
    "external_dependencies": {
        "python": [
            "requests_toolbelt",
            "pandas",
            "lxml_to_dict",
            "pycryptodome",
            "html2text",
        ],
    },
    "qweb": ["static/src/xml/*.xml",],
    "license": "LGPL-3",
    # "post_init_hook": "post_init_hook",
}

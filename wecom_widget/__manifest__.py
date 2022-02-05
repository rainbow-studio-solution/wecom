# -*- coding: utf-8 -*-

{
    "name": "WeCom Widget",
    "author": "RStudio",
    "category": "WeCom/WeCom",
    "summary": "WeCom Widget",
    "website": "https://gitee.com/rainbowstudio/wxwork",
    "version": "14.0.0.1",
    "description": """ 

""",
    "depends": [
        "web",
    ],
    "data": [
        # "views/assets_templates.xml",
    ],
    "assets": {
        "web.assets_backend":[
            # SCSSS
            "wecom_widget/static/src/scss/jsoneditor.scss",
            "wecom_widget/static/src/scss/dialog.scss",
            "wecom_widget/static/src/scss/showpassword.scss",
            # js
            "wecom_widget/static/src/js/wecom_markdown.js",
            "wecom_widget/static/src/js/show_password.js",
            "wecom_widget/static/src/js/fields_wecom_message_widget.js",
            "wecom_widget/static/src/js/wecom_widget_image_url.js",
            "wecom_widget/static/src/js/jsoneditor.js",
            "wecom_widget/static/src/js/dialog.js",
        ],
        "web.assets_qweb": [
            'wecom_widget/static/src/xml/*.xml',
        ],
    },

    "sequence": 605,
    "installable": True,
    "auto_install": False,
    "application": False,
    "license": "LGPL-3",
}

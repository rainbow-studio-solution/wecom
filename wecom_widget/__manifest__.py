# -*- coding: utf-8 -*-

{
    "name": "WeCom Widget",
    "author": "RStudio",
    "category": "WeCom Suites/Widget",
    "summary": "WeCom Widget",
    "website": "https://gitee.com/rainbowstudio/wecom",
    "version": "15.0.0.1",
    "description": """ 

""",
    "depends": ["web",],
    "data": [
        # "views/assets_templates.xml",
    ],
    "assets": {
        "web.assets_backend": [
            # SCSSS
            "wecom_widget/static/src/scss/jsoneditor.scss",
            "wecom_widget/static/src/scss/dialog.scss",
            "wecom_widget/static/src/scss/showpassword.scss",
            "wecom_widget/static/src/scss/wecom_config.scss",
            "wecom_widget/static/src/legacy/scss/wecom_pro_tag.scss",
            # js
            "wecom_widget/static/src/legacy/js/fields/wecom_pro_tag.js",
            "wecom_widget/static/src/js/wecom_markdown.js",
            "wecom_widget/static/src/js/show_password.js",
            "wecom_widget/static/src/js/fields_wecom_message_widget.js",
            "wecom_widget/static/src/js/wecom_widget_image_url.js",
            "wecom_widget/static/src/js/jsoneditor.js",
            "wecom_widget/static/src/js/dialog.js",
            "wecom_widget/static/src/js/wecom_config.js",
        ],
        "web.assets_qweb": ["wecom_widget/static/src/xml/*.xml",],
    },
    "sequence": 600,
    "installable": True,
    "auto_install": False,
    "application": False,
    "license": "LGPL-3",
}

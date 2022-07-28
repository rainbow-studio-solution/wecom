# -*- coding: utf-8 -*-

{
    "name": "Web multi level menu",
    "category": "Extra Tools",
    "version": "15.0.0.1",
    "summary": "Let odoo support more than 4 levels of menus.",
    "description": """""",
    "author": "RStudio",
    "website": "https://gitee.com/rainbowstudio/wecom",
    "depends": ["web"],
    "installable": True,
    "application": True,
    "auto_install": False,
    "data": [],
    "assets": {
        "web._assets_common_styles": [
            "web_multi_level_menu/static/src/webclient/navbar/navbar.scss",
        ],
        "web.assets_qweb": [
            "web_multi_level_menu/static/src/webclient/navbar/navbar.xml",
        ],
    },
    "images": ["static/description/images/main_screenshot.png"],
    "license": "LGPL-3",
}

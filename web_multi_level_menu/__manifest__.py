# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Web multi level menu",
    "category": "Hidden",
    "version": "15.0.0.1",
    "summary": "Let odoo support more than 4 levels of menus.",
    "description": """""",
    "author": "RStudio",
    "website": "https://gitee.com/rainbowstudio/wecom",
    "depends": ["web"],
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
    "license": "LGPL-3",
}

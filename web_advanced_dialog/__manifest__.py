# -*- coding: utf-8 -*-
{
    "name": "Web Advanced Dialog",
    "author": "RStudio",
    "website": "",
    "sequence": 1,
    "installable": True,
    "application": False,
    "auto_install": False,
    "category": "Hidden",
    "version": "14.0.0.1",
    "summary": """
        
        """,
    "description": """
本模块参考了  https://loney-cao.github.io/2019/11/28/odoo13_5/  的资料


如何使用:
----------------------------------------------

**示例:在Python代码中使用**

::

    return {
        "type": "ir.actions.client",
        "tag": "dialog",
        "params": {
            "title": _("Successful operation"),
            "$content": _(
                "<div>Successfully obtained corporate WeChat contact token.</div>"
            ),
            "size": "medium",
            "reload": "true",
        },
    }

选项说明： 
----------------------------------------------

-title              标题

-content           弹框内容，必须使用html标签包裹

-size               大小

-reload             点击按钮后是否刷新页面


联系我： 
----------------------------------------------
rain.wen@outlook.com

        """,
    "depends": ["web",],
    "external_dependencies": {"python": [],},
    "data": ["views/assets_templates.xml",],
    "qweb": [
        # "static/src/xml/*.xml",
    ],
}

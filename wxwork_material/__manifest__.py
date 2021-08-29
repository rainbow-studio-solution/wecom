# -*- coding: utf-8 -*-
{
    "name": "Enterprise WeChat Material",
    "author": "RStudio",
    "website": "https://gitee.com/rainbowstudio/wxwork",
    "sequence": 606,
    "installable": True,
    "application": True,
    "auto_install": False,
    "category": "Enterprise WeChat/Enterprise WeChat",
    "version": "14.0.0.1",
    "summary": """
        Enterprise WeChat material management 
        """,
    "description": """
please make sure ffmpeg, sox, and mediainfo are installed on your system, e.g.

DOC:
=============

* https://github.com/jiaaro/pydub

Install:
=============

::

    # libav
    apt-get install libav-tools libavcodec-extra

    # ffmpeg
    apt-get install ffmpeg libavcodec-extra

    # pydub
    pip install pydub

""",
    "depends": ["attachment_indexation", "wxwork_smart_hrm"],
    "data": [
        "security/ir.model.access.csv",
        "data/material_data.xml",
        "views/material_views.xml",
        "views/res_company_views.xml",
        "views/menu.xml",
    ],
    "external_dependencies": {"python": ["ffmpy", "pydub", "requests_toolbelt"],},
    "qweb": ["static/src/xml/*.xml",],
}

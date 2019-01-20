# -*- encoding: utf-8 -*-
#                                                                            #
#   OpenERP Module                                                           #
#   Copyright (C) 2013 Author <email@email.fr>                               #
#                                                                            #
#   This program is free software: you can redistribute it and/or modify     #
#   it under the terms of the GNU Affero General Public License as           #
#   published by the Free Software Foundation, either version 3 of the       #
#   License, or (at your option) any later version.                          #
#                                                                            #
#   This program is distributed in the hope that it will be useful,          #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#   GNU Affero General Public License for more details.                      #
#                                                                            #
#   You should have received a copy of the GNU Affero General Public License #
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.    #
#                                                                            #

{
    "name": "Dingtalk Oauth",
    "version": "11.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["base", "auth_oauth", "base_setup"],
    "author": "山西清水欧度信息技术有限公司",
    'website': 'http://www.odooqs.com',
    "category": "Tools",
    "description": """
    """,
    "data": [
        'views/res_config_settings_view.xml',
    ],
    "init_xml": [],
    'update_xml': [],
    'demo_xml': [],
    'images': ['static/description/banner.jpg','static/description/main_screenshot.png'],
    'installable': True,
    'active': False,
    #    'certificate': '',
}

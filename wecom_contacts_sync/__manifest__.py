# -*- coding: utf-8 -*-
{
    "name": "WeCom Contacts Synchronized",
    "author": "RStudio",
    "website": "https://eis-solution.coding.net/public/odoo/oec/git",
    "sequence": 603,
    "installable": True,
    "application": True,
    "auto_install": False,
    "category": "WeCom Suites/CRM",
    "version": "16.0.0.1",
    "summary": """

        """,
    "description": """


        """,
    "depends": [
        "wecom_contacts",
        "hr",
    ],
    "external_dependencies": {
        "python": ["pandas"],
    },
    "data": [
        "security/ir.model.access.csv",
        "data/wecom_app_config_data.xml",
        "data/wecom_app_event_type_data.xml",
        "data/ir_cron_data.xml",
        "data/hr_data.xml",
        "wizard/employee_bind_wecom_views.xml",
        "wizard/user_bind_wecom_views.xml",
        "wizard/wecom_contacts_sync_wizard_views.xml",
        "wizard/wecom_users_sync_wizard_views.xml",
        "views/wecom_user_views.xml",
        "views/wecom_department_views.xml",
        "views/wecom_tag_views.xml",
        "views/wecom_contacts_block_views.xml",
        "views/res_config_settings_views.xml",
        "views/res_users_views.xml",
        "views/wecom_apps_views.xml",
        "views/hr_department_view.xml",
        "views/hr_employee_view.xml",
        "views/hr_employee_category_views.xml",
        "views/ir_cron_views.xml",
        "views/menu_views.xml",
    ],
    "assets": {
        "web._assets_common_styles": [
            "wecom_contacts_sync/static/src/scss/sync_result_dialog.scss",
        ],
        "web.assets_backend": [
            # SCSSS
            # JS
            # "wecom_contacts_sync/static/src/js/*.js",
        ],
    },
    "license": "AGPL-3",
}

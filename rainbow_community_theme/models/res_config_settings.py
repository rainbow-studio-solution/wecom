# -*- coding: utf-8 -*-

import logging
import base64
import io

from odoo.tools.misc import file_open
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.modules.module import get_resource_path
from random import randrange
from PIL import Image


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # 全局设置
    system_name = fields.Char('System Name',
                              help="Setup System Name",
                              translate=True,
                              config_parameter='rainbow.system_name',
                              default="ERP Solution")
    show_lang = fields.Boolean(
        'Show Quick Language Switcher',
        translate=True,
        help="When enable,User can quick switch language in user menu")
    show_poweredby = fields.Boolean('Show Powered by Text',
                                    translate=True,
                                    help="Uncheck to hide the Powered by text")
    poweredby_text = fields.Char(
        'Customize Powered by text(eg. Powered by Odoo)',
        translate=True,
        config_parameter='rainbow.poweredby_text',
        default="Powered by Odoo")
    poweredby_url = fields.Char(
        'Customize Powered by Url(eg. https://www.odoo.com)',
        config_parameter='rainbow.poweredby_url',
        default='https://www.odoo.com')
    web_icon = fields.Char('Web Favicon Icon',
                           config_parameter='rainbow.web_icon',
                           default='static/src/img/favicon.png')
    apple_icon = fields.Char(
        'Apple Touch Icon',
        config_parameter='rainbow.apple_touch_icon',
        default=
        '/rainbow_community_theme/static/src/img/mobile-icons/apple-152x152.png'
    )
    android_icon = fields.Char(
        'Android Touch Icon',
        config_parameter='rainbow.android_touch_icon',
        default=
        '/rainbow_community_theme/static/src/img/mobile-icons/android-192x192.png'
    )
    windows_icon = fields.Char(
        'Windows Touch Icon',
        config_parameter='rainbow.windows_touch_icon',
        default=
        '/rainbow_community_theme/static/src/img/mobile-icons/windows-144x144.png'
    )

    # 用户菜单
    show_debug = fields.Boolean(
        'Show Quick Debug',
        translate=True,
        help="When enable,everyone login can see the debug menu")
    show_documentation = fields.Boolean(
        'Show Documentation',
        translate=True,
        help="When enable,User can visit user manual")
    show_documentation_dev = fields.Boolean(
        'Show Developer Documentation',
        translate=True,
        help="When enable,User can visit development documentation")
    show_support = fields.Boolean(
        'Show Support',
        translate=True,
        help="When enable,User can vist your support site")
    show_account = fields.Boolean(
        'Show My Account',
        translate=True,
        help="When enable,User can login to your website")

    documentation_url = fields.Char(
        'Documentation Url',
        config_parameter='rainbow.documentation_url',
        default='https://www.odoo.com/documentation/user')
    documentation_dev_url = fields.Char(
        'Developer Documentation Url',
        config_parameter='rainbow.documentation_dev_url',
        default='https://www.odoo.com/documentation')
    support_url = fields.Char('Support Url',
                              config_parameter='rainbow.support_url',
                              default='https://www.odoo.com/buy')
    account_title = fields.Char('Account Title',
                                translate=True,
                                config_parameter='rainbow.account_title',
                                default='My Online Account')
    account_url = fields.Char('Account Url',
                              config_parameter='rainbow.account_url',
                              default='https://accounts.odoo.com/account')

    # 应用设置
    # show_enterprise = fields.Boolean('Show Enterprise Tag',
    #                                  translate=True,
    #                                  help="Uncheck to hide the Enterprise tag")
    # show_share = fields.Boolean(
    #     'Show Share Dashboard',
    #     translate=True,
    #     help="Uncheck to hide the Odoo Share Dashboard")
    # group_show_author_in_apps = fields.Boolean(
    #     string="Show Author in Apps Dashboard",
    #     implied_group='rainbow_community_theme.group_show_author_in_apps',
    #     translate=True,
    #     help="Uncheck to Hide Author and Website in Apps Dashboard")
    # enterprise_url = fields.Char('Customize Module Url(eg. Enterprise)',
    #                              config_parameter='rainbow.enterprise_url',
    #                              default='https://www.odoo.com')

    # module_rainbow_auth_oauth = fields.Boolean(
    #     "Use external authentication providers (OAuth)")
    # module_rainbow_auth_signup = fields.Boolean(
    #     "Enable password reset from Login page")

    # 主题
    enable_login_theme = fields.Boolean(
        'Enable login theme',
        default=True,
        translate=True,
        help='Uncheck to hide the customize login themes')
    login_theme = fields.Selection(
        [('1', 'Theme 1'), ('2', 'Theme 2'), ('3', 'Theme 3'),
         ('4', 'Theme 4'), ('5', 'Theme 5'), ('6', 'Theme 6')],
        'Login Theme',
        required=True,
        translate=True,
        config_parameter='rainbow.login_theme',
    )
    # lock_theme = fields.Selection(
    #     [('1', 'Theme 1'), ('2', 'Theme 2')],
    #     'Lock Theme',
    #     required=True,
    #     translate=True,
    #     config_parameter='rainbow.lock_theme',
    # )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ir_config = self.env['ir.config_parameter'].sudo()
        # 全局设置
        show_lang = True if ir_config.get_param(
            'rainbow.show_lang') == "True" else False
        # system_name = True if ir_config.get_param(
        #     'rainbow.system_name') == "True" else False
        show_poweredby = True if ir_config.get_param(
            'rainbow.show_poweredby') == "True" else False
        # poweredby_text = True if ir_config.get_param(
        #     'rainbow.poweredby_text') == "True" else False
        # poweredby_url = True if ir_config.get_param(
        #     'rainbow.poweredby_url') == "True" else False

        # 用户菜单
        show_debug = True if ir_config.get_param(
            'rainbow.show_debug') == "True" else False
        show_documentation = True if ir_config.get_param(
            'rainbow.show_documentation') == "True" else False
        show_documentation_dev = True if ir_config.get_param(
            'rainbow.show_documentation_dev') == "True" else False
        show_support = True if ir_config.get_param(
            'rainbow.show_support') == "True" else False
        show_account = True if ir_config.get_param(
            'rainbow.show_account') == "True" else False

        # 应用
        # show_enterprise = True if ir_config.get_param(
        #     'rainbow.show_enterprise') == "True" else False
        # show_share = True if ir_config.get_param(
        #     'rainbow.show_share') == "True" else False
        # enterprise_url = ir_config.get_param('rainbow.enterprise_url', default='https://www.odoo.com')

        # 主题
        login_theme = ir_config.get_param('rainbow.login_theme', default='4')
        enable_login_theme = True if ir_config.get_param(
            'rainbow.enable_login_theme') == "True" else False

        res.update(
            # system_name=system_name,
            show_lang=show_lang,
            show_debug=show_debug,
            show_poweredby=show_poweredby,
            # poweredby_text=poweredby_text,
            # poweredby_url=poweredby_url,
            show_documentation=show_documentation,
            show_documentation_dev=show_documentation_dev,
            show_support=show_support,
            show_account=show_account,
            # show_enterprise=show_enterprise,
            # show_share=show_share,
            enable_login_theme=enable_login_theme,
            login_theme=login_theme

            # documentation_url=documentation_url,
            # documentation_dev_url=documentation_dev_url,
            # support_url=support_url,
            # account_title=account_title,
            # account_url=account_url,
            # enterprise_url=enterprise_url,
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ir_config = self.env['ir.config_parameter'].sudo()
        ir_config.set_param("rainbow.system_name", self.system_name
                            or "ERP Solution")
        ir_config.set_param("rainbow.show_lang", self.show_lang or "False")
        ir_config.set_param("rainbow.show_debug", self.show_debug or "False")
        ir_config.set_param("rainbow.show_poweredby", self.show_poweredby
                            or "False")
        ir_config.set_param("rainbow.poweredby_text", self.poweredby_text
                            or "False")
        ir_config.set_param("rainbow.poweredby_url", self.poweredby_url
                            or "False")
        ir_config.set_param("rainbow.show_documentation",
                            self.show_documentation or "False")
        ir_config.set_param("rainbow.show_documentation_dev",
                            self.show_documentation_dev or "False")
        ir_config.set_param("rainbow.show_support", self.show_support
                            or "False")
        ir_config.set_param("rainbow.show_account", self.show_account
                            or "False")
        # ir_config.set_param("rainbow.show_enterprise", self.show_enterprise
        #                     or "False")
        # ir_config.set_param("rainbow.show_share", self.show_share or "False")

        ir_config.set_param("rainbow.enable_login_theme",
                            self.enable_login_theme or "False")

        # ir_config.set_param("rainbow.documentation_url",
        #                     self.documentation_url or "https://www.odoo.com/documentation/user")
        # ir_config.set_param("rainbow.documentation_dev_url",
        #                     self.documentation_dev_url or "https://www.odoo.com/documentation")
        # ir_config.set_param("rainbow.support_url", self.support_url or "https://www.odoo.com/buy")
        # ir_config.set_param("rainbow.account_title", self.account_title or "My Online Account")
        # ir_config.set_param("rainbow.account_url", self.account_url or "https://accounts.odoo.com/account")
        # ir_config.set_param("rainbow.enterprise_url", self.enterprise_url or "https://www.odoo.com")
        # ir_config.set_param("rainbow.poweredby_text", self.poweredby_text or "Odoo")
        # ir_config.set_param("rainbow.poweredby_url", self.poweredby_url or "https://www.odoo.com")
        # ir_config.set_param("rainbow.login_theme", self.login_theme or "4")

    def set_values_module_url(self):
        sql = "UPDATE ir_module_module SET website = '%s' WHERE license like '%s' and website <> ''" % (
            self.enterprise_url, 'OEEL%')
        try:
            self._cr.execute(sql)
            self._cr.commit()
        except Exception as e:
            pass

    def hide_enterprise_apps(self):
        sql = "UPDATE ir_module_module SET application=FALSE  WHERE to_buy=TRUE"
        try:
            self._cr.execute(sql)
            self._cr.commit()
        except Exception as e:
            pass
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def show_enterprise_apps(self):
        sql = "UPDATE ir_module_module SET application=TRUE  WHERE to_buy=TRUE"
        try:
            self._cr.execute(sql)
            self._cr.commit()
        except Exception as e:
            pass
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def uninstall_odoo_referral_program(self):
        try:
            self.env['ir.module.module'].search([
                ('name', '=', 'odoo_referral')
            ]).button_immediate_uninstall()
        except Exception as e:
            pass
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def set_values_company_favicon(self):
        company = self.sudo().env['res.company']
        records = company.search([])

        if len(records) > 0:
            for record in records:
                record.write({'favicon': self._set_web_favicon(original=True)})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def _set_web_favicon(self, original=False):
        ir_config = self.env['ir.config_parameter'].sudo()
        favicon = ir_config.get_param('rainbow.web_icon')
        if not favicon:
            img_path = get_resource_path('rainbow_community_theme',
                                         'static/src/img/favicon.png')
        else:
            img_path = get_resource_path('rainbow_community_theme', favicon)

        with tools.file_open(img_path, 'rb') as f:
            if original:
                return base64.b64encode(f.read())

            color = (randrange(32, 224,
                               24), randrange(32, 224,
                                              24), randrange(32, 224, 24))
            original = Image.open(f)
            new_image = Image.new('RGBA', original.size)
            height = original.size[1]
            width = original.size[0]
            bar_size = 1
            for y in range(height):
                for x in range(width):
                    pixel = original.getpixel((x, y))
                    if height - bar_size <= y + 1 <= height:
                        new_image.putpixel((x, y),
                                           (color[0], color[1], color[2], 255))
                    else:
                        new_image.putpixel(
                            (x, y), (pixel[0], pixel[1], pixel[2], pixel[3]))
            stream = io.BytesIO()
            new_image.save(stream, format="ICO")
            return base64.b64encode(stream.getvalue())

        self.env['ir.http'].clear_caches()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
import lxml.etree as et
# from lxml import etree
# from lxml.etree import LxmlError
# from lxml.builder import E


class Users(models.Model):
    _inherit = 'res.users'

    theme_color = fields.Char(string='Theme Color', default='default')
    launcher_bg_status = fields.Char(
        string='Enable/Disable Launcher Background', default='enable')
    launcher_bg = fields.Char(string='Launcher Background', default='8.jpg')
    submenu_position = fields.Char(string='Submenu display position',
                                   default='sidebar')
    sidebar_mode = fields.Char(string='Sidebar Mode', default='expand')
    sidebar_position = fields.Char(string='Sidebar Position', default='left')
    theme_footer = fields.Char(string='Show Footer', default='show')

    # common_apps = fields.Text(string='Common Apps', default='[]')
    # common_app_quantity = fields.Char(string='Common Apps Quantity',
    #                                   default='5')

    def set_theme(self, args=None):
        # view = self.sudo().env['ir.ui.view']
        # record = view.search([
        #     ('key', '=', 'rainbow_community_theme._assets_primary_variables')
        # ])
        # tree = et.fromstring(record['arch_db'])

        # for el in tree.xpath("//link[@id='style_color']"):
        #     el.attrib['href'] = '/rainbow_community_theme/themes/' + args[
        #         'theme_color'] + '/eis_theme.scss'

        # record.write({
        #     'arch_db': et.tostring(tree),
        # })

        result = self.sudo().write(args)

        self.env['res.users'].clear_caches()
        self.env['ir.http'].clear_caches()

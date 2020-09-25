# -*- coding: utf-8 -*-

import lxml.etree as et

tree = et.fromstring('''
<data inherit_id="web._assets_primary_variables" priority="15">
        <xpath expr="//link[last()]" position="after">
            <link rel="stylesheet" type="text/scss" href="/rainbow_community_theme/static/src/scss/themes/primary_variables.scss"/>
            <link id="style_color" rel="stylesheet" type="text/scss" href="/rainbow_community_theme/static/src/scss/themes/default/eis_theme.scss"/>
        </xpath>
</data>
''')

for el in tree.xpath("//link[@id='style_color']"):
    el.attrib['href'] = '/rainbow_community_theme/themes/dk/eis_theme.scss'
print(et.tostring(tree))

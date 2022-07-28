==============================================
Web multi level menu
==============================================


Introduce:
----------------------------------------------
* Used to display menus with more than four levels.

----


How to install:
----------------------------------------------
1) Click on the menu "Apps".
2) Select "Extra" in the filter popup menu.
3) Enter "web_multi_level_menu" in the search input box.
4) Please install the module "Web multi level menu" in the search results.

----

code demo:
----------------------------------------------
* Code file path: /web_multi_level_menu/static/src/webclient/navbar/navbar.xml

**Example1:Modify the form view in debug mode**

::

    <t t-inherit="web.NavBar.SectionsMenu.Dropdown.MenuSlot" t-inherit-mode="extension" owl="1">
        <xpath expr="t[@t-foreach='items']" position="replace">
            <t t-foreach="items" t-as="item" t-key="item.id">
                <t t-if="!item.childrenTree.length">
                    <MenuItem payload="item" href="getMenuItemHref(item)" class="dropdown-item" t-esc="item.name" />
                </t>
                <t t-else="">
                    <div class="dropdown-menu_group dropdown-header" t-esc="item.name" />
                    <t t-foreach="item.childrenTree" t-as="subItem" t-key="subItem.id">
                        <t t-if="!subItem.childrenTree.length">
                            <MenuItem class="o_dropdown_menu_group_entry dropdown-item" payload="subItem" href="getMenuItemHref(subItem)" t-esc="subItem.name" />
                        </t>
                        <t t-else="">
                            <div class="dropdown-menu_group o_dropdown_fifth_menu_group_header dropdown-header" t-esc="subItem.name" />
                            <!-- Level 5 submenu -->
                            <t t-foreach="subItem.childrenTree" t-as="subSubItem" t-key="subSubItem.id">
                                <MenuItem class="o_dropdown_menu_group_entry o_dropdown_fifth_menu_group dropdown-item" payload="subSubItem" href="getMenuItemHref(subSubItem)" t-esc="subSubItem.name" />
                            </t>
                        </t>
                    </t>
                </t>
            </t>
        </xpath>
    </t>


----





Bugs and requirements:
----------------------------------------------

You can send an email to rain.wen@outlook.com to submit bugs and requirements to me.

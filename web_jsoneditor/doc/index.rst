==============================================
Web Json Editor
==============================================

Features:
----------------------------------------------
* view, edit, format and validate JSON.
* It has multiple modes, such as tree editor, code editor and plain text editor. 


----



How to install:
----------------------------------------------
1) Click on the menu "Apps".
2) Enter "Web Json Editor" in the search input box.
3) Please install the module "Web Json Editor" in the search results.

----

How to use in form view:
----------------------------------------------
* You can directly modify the form view in odoo debug mode.
* You can inherit the view and use position="attributes" to add widget="jsoneditor" to the field.

**Example1:Modify the form view in debug mode**

::

    <field name="arch" type="xml">
        <form string="View name">
            <field name="json" widget="jsoneditor" options="{'modes':  ['text', 'code', 'tree', 'form', 'view', 'preview'], 'darktheme':false}" />
        </form>
    </field>

**Example2:Inherit the view to add attributes to the field**

::

    <xpath expr="//field[@name='json']" position="attributes">
        <attribute name="widget">jsoneditor</attribute>
        <attribute name="options">{'modes':  ['text', 'code', 'tree', 'form', 'view', 'preview'], 'darktheme':false}</attribute>
    </xpath>

----

Options description:
----------------------------------------------

-modes           Editor mode, if it is empty, the default is ['text', 'code', 'tree', 'form', 'view', 'preview'].
-darktheme       Use dark theme, Default true





Bugs and requirements:
----------------------------------------------

You can send an email to rain.wen@outlook.com to submit bugs and requirements to me.

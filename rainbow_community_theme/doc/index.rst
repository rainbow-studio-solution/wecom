==============================================
Using Help
==============================================

How to install:
----------------------------------------------
1) Click on the menu "Apps".
2) Select "Extra" in the filter popup menu.
3) Enter "Rainbow Community Theme" in the search input box.
4) Please install the module "Rainbow Community Theme" in the search results.


Disable customized database management:
----------------------------------------------
1) Open path:/rainbow_community_theme/controllers/__init__.py
2) Comment out ‘from. Import database’

Custom Login Page Background Picture:
----------------------------------------------
*Open path:/rainbow_community_theme/static/src/js/login , login4.js \ login5.js \ login6.js*

**Example:**

::

    $.backstretch([
        "/rainbow_community_theme/static/src/img/bg/1.jpg",
        "/rainbow_community_theme/static/src/img/bg/2.jpg",
        "/rainbow_community_theme/static/src/img/bg/3.jpg",
        "/rainbow_community_theme/static/src/img/bg/4.jpg"
    ],{
        fade: 1000,
        duration: 8000
        },
    );


Custom Web Favicon Icon
----------------------------------------------
1) Please upload the icon to the module 'rainbow_community_theme' static directory, (eg. 'static/src/img/') 
2) Settings >> Base settings >> Web Favicon Icon
3) Click to set web favicon icon

View log
----------------------------------------------

:: 

    tail -f /var/log/odoo/odoo-server.log 

Error Solution
----------------------------------------------
1) ValueError: Unknown path: /web/static/lib/moment/locale/en-us.js,  Copy files 'web/static/lib/moment/locale/en-gb.js' and rename it to ‘web/static/lib/moment/locale/en-us.js’

Bugs and requirements:
----------------------------------------------

You can send an email to rain.wen@outlook.com to submit bugs and requirements to me.

如果你是汉语使用者，直接使用中文吧。我在武汉，愿世界安详，世道够艰难的。
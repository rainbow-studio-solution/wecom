odoo.define('wxwork_base.WXWorkSettingsNavigationMenu', function (require) {
    'use strict';

    var Widget = require('web.Widget');
    var widget_registry = require('web.widget_registry');

    var WXWorkSettingsNavigationMenu = Widget.extend({
        template: 'res_config_wxwork_navigation_menu',
        events: {
            'click a.wxwork_jump_anchor': '_jump_anchor',
        },
        init: function () {
            this._super.apply(this, arguments);
        },
        start: function () {
            return this._super.apply(this, arguments);
        },
        _jump_anchor: function (ev) {
            ev.preventDefault(); //阻止默认行为
            var anchor = $(ev.target).attr('href');

            if ($(ev.target).prop("tagName") != "A") {
                anchor = $(ev.target).parent().attr('href');
            }

            var settingsEl = this.$el.parents(".settings");
            var wxworkSettingsEl = this.$el.parents(".app_settings_block");

            if (wxworkSettingsEl.height() > settingsEl.height()) {
                settingsEl.animate({
                    scrollTop: $(anchor).position().top,
                }, 1000)
            }
        }
    });
    widget_registry.add('res_config_wxwork_navigation_menu', WXWorkSettingsNavigationMenu);
    return WXWorkSettingsNavigationMenu;
});


odoo.define('wxwork_base.WXWorkSettingsNavigationGoTop', function (require) {
    'use strict';

    var Widget = require('web.Widget');
    var widget_registry = require('web.widget_registry');

    var WXWorkSettingsNavigationGoTop = Widget.extend({
        template: 'res_config_wxwork_navigation_gotop',
        events: {
            'click': '_gotop',
        },
        init: function () {
            this._super.apply(this, arguments);
        },
        start: function () {
            return this._super.apply(this, arguments);
        },
        _gotop: function (ev) {
            ev.preventDefault(); //阻止默认行为
            var settingsEl = this.$el.parents(".settings");
            var wxworkSettingsEl = this.$el.parents(".app_settings_block");

            if (wxworkSettingsEl.height() > settingsEl.height()) {
                settingsEl.animate({
                    scrollTop: $("#wxwork_global").position().top,
                }, 1000)
            }
        }
    });
    widget_registry.add('res_config_wxwork_navigation_gotop', WXWorkSettingsNavigationGoTop);
    return WXWorkSettingsNavigationGoTop;
});

odoo.define('wxwork_base.WXWorkSettingsNavigationGoBottom', function (require) {
    'use strict';

    var Widget = require('web.Widget');
    var widget_registry = require('web.widget_registry');

    var WXWorkSettingsNavigationGoBottom = Widget.extend({
        template: 'res_config_wxwork_navigation_gobottom',
        events: {
            'click': '_gobottom',
        },
        init: function () {
            this._super.apply(this, arguments);
        },
        start: function () {
            return this._super.apply(this, arguments);
        },
        _gobottom: function (ev) {
            ev.preventDefault(); //阻止默认行为

            var settingsEl = this.$el.parents(".settings");
            var wxworkSettingsEl = this.$el.parents(".app_settings_block");

            if (wxworkSettingsEl.height() > settingsEl.height()) {
                settingsEl.animate({
                    scrollTop: $("#wxwork_bottom").position().top,
                }, 1000)
            }
        }
    });
    widget_registry.add('res_config_wxwork_navigation_gobottom', WXWorkSettingsNavigationGoBottom);
    return WXWorkSettingsNavigationGoBottom;
});
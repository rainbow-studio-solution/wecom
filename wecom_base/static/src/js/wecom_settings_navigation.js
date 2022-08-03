odoo.define('wecom_base.WecomSettingsNavigationMenu', function (require) {
    'use strict';

    var Widget = require('web.Widget');
    var widget_registry = require('web.widget_registry');

    var WecomSettingsNavigationMenu = Widget.extend({
        template: 'res_config_wecom_navigation_menu',
        events: {
            'click a.wecom_jump_anchor': '_jump_anchor',
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
            var wecomSettingsEl = this.$el.parents(".app_settings_block");
            if ($(anchor).length > 0) {
                if (wecomSettingsEl.height() > settingsEl.height()) {
                    settingsEl.animate({
                        scrollTop: $(anchor).position().top,
                    }, 1000)
                }
            }
        }
    });
    widget_registry.add('res_config_wecom_navigation_menu', WecomSettingsNavigationMenu);
    return WecomSettingsNavigationMenu;
});


odoo.define('wecom_base.WeComSettingsNavigationGoTop', function (require) {
    'use strict';

    var Widget = require('web.Widget');
    var widget_registry = require('web.widget_registry');

    var WeComSettingsNavigationGoTop = Widget.extend({
        template: 'res_config_wecom_navigation_gotop',
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
            var wecomSettingsEl = this.$el.parents(".app_settings_block");

            if (wecomSettingsEl.height() > settingsEl.height()) {
                settingsEl.animate({
                    scrollTop: $("#wecom_settings_navigation").position().top,
                }, 1000)
            }
        }
    });
    widget_registry.add('res_config_wecom_navigation_gotop', WeComSettingsNavigationGoTop);
    return WeComSettingsNavigationGoTop;
});

odoo.define('wecom_base.WeComSettingsNavigationGoBottom', function (require) {
    'use strict';

    var Widget = require('web.Widget');
    var widget_registry = require('web.widget_registry');

    var WeComSettingsNavigationGoBottom = Widget.extend({
        template: 'res_config_wecom_navigation_gobottom',
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
            var wecomSettingsEl = this.$el.parents(".app_settings_block");

            if (wecomSettingsEl.height() > settingsEl.height()) {
                settingsEl.animate({
                    scrollTop: $("#wecom_bottom").position().top,
                }, 1000)
            }
        }
    });
    widget_registry.add('res_config_wecom_navigation_gobottom', WeComSettingsNavigationGoBottom);
    return WeComSettingsNavigationGoBottom;
});
odoo.define('hrms_base.WecomSettingsNavigationMenu', function (require) {
    'use strict';

    var Widget = require('web.Widget');
    var widget_registry = require('web.widget_registry');

    var WecomSettingsNavigationMenu = Widget.extend({
        template: 'res_config_hrms_navigation_menu',
        events: {
            'click a.hrms_jump_anchor': '_jump_anchor',
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
            var hrmsSettingsEl = this.$el.parents(".app_settings_block");
            if ($(anchor).length > 0) {
                if (hrmsSettingsEl.height() > settingsEl.height()) {
                    settingsEl.animate({
                        scrollTop: $(anchor).position().top,
                    }, 1000)
                }
            }
        }
    });
    widget_registry.add('res_config_hrms_navigation_menu', WecomSettingsNavigationMenu);
    return WecomSettingsNavigationMenu;
});


odoo.define('hrms_base.WeComSettingsNavigationGoTop', function (require) {
    'use strict';

    var Widget = require('web.Widget');
    var widget_registry = require('web.widget_registry');

    var WeComSettingsNavigationGoTop = Widget.extend({
        template: 'res_config_hrms_navigation_gotop',
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
            var hrmsSettingsEl = this.$el.parents(".app_settings_block");

            if (hrmsSettingsEl.height() > settingsEl.height()) {
                settingsEl.animate({
                    scrollTop: $("#hrms_menu").position().top,
                }, 1000)
            }
        }
    });
    widget_registry.add('res_config_hrms_navigation_gotop', WeComSettingsNavigationGoTop);
    return WeComSettingsNavigationGoTop;
});

odoo.define('hrms_base.HrmsSettingsNavigationGoBottom', function (require) {
    'use strict';

    var Widget = require('web.Widget');
    var widget_registry = require('web.widget_registry');

    var HrmsSettingsNavigationGoBottom = Widget.extend({
        template: 'res_config_hrms_navigation_gobottom',
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
            var hrmsSettingsEl = this.$el.parents(".app_settings_block");

            if (hrmsSettingsEl.height() > settingsEl.height()) {
                settingsEl.animate({
                    scrollTop: $("#hrms_bottom").position().top,
                }, 1000)
            }
        }
    });
    widget_registry.add('res_config_hrms_navigation_gobottom', HrmsSettingsNavigationGoBottom);
    return HrmsSettingsNavigationGoBottom;
});
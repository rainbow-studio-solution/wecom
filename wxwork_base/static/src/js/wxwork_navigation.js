odoo.define('wxwork_base.Anchor', function (require) {
    'use strict';

    var ActionManager = require('web.ActionManager');
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
            var self = this;
            return this._super.apply(this, arguments);
        },
        _jump_anchor: function (ev) {
            ev.preventDefault(); //阻止默认行为
            var self = this;
            var anchor = $(ev.target).attr('href');

            if ($(ev.target).prop("tagName") != "A") {
                anchor = $(ev.target).parent().attr('href');
            }

            var settingsEl = this.$el.parents(".settings");
            var wxworkSettingsEl = this.$el.parents(".app_settings_block");
            var navEl = this.$el;

            // var $settings = this.$el.parents(".app_settings_block");
            console.log($(anchor).offset().top, navEl.outerHeight());
            console.log($(anchor).offset().top - navEl.outerHeight());

            if (wxworkSettingsEl.height() > settingsEl.height()) {
                // settingsEl.animate({
                //     scrollTop: $(anchor).offset().top - navEl.outerHeight(),
                // }, 1000)
                settingsEl.scrollTop($(anchor).offset().top - navEl.outerHeight());
            }

        }
    });
    widget_registry.add('res_config_wxwork_navigation_menu', WXWorkSettingsNavigationMenu);
    return WXWorkSettingsNavigationMenu;
});
odoo.define('wxwork_base.Anchor', function (require) {
    'use strict';

    var Widget = require('web.Widget');
    var widget_registry = require('web.widget_registry');
    var WXWorkSettingsAnchor = Widget.extend({
        // selector: 'div.app_settings_block',
        template: 'res_config_wxwork_anchor',
        events: {
            'click a.wxwork_jump_anchor': '_jump_anchor',
        },
        init: function () {
            this._super.apply(this, arguments);
        },
        start: function () {
            console.log(this.$el);
            var self = this;
            return this._super.apply(this, arguments);
        },
        _jump_anchor: function (ev) {
            ev.preventDefault(); //阻止默认行为
            var self = this;
            var anchor = $(ev.target).attr('href');

            if ($(ev.target).prop("tagName") == "H5") {
                anchor = $(ev.target).parent().attr('href');

            }
            console.log("点击", anchor);
        }
    });
    widget_registry.add('res_config_wxwork_anchor', WXWorkSettingsAnchor);
    return WXWorkSettingsAnchor;
});
odoo.define('rainbow_community_theme.DebugManager', function (require) {
    "use strict";

    var config = require('web.config');
    var WebClient = require('web.WebClient');

    if (config.isDebug()) {
        WebClient.include({
            start: function () {
                var self = this;
                return this._super.apply(this, arguments).then(function () {
                    // Override toggle_launcher_menu to trigger an event to update the debug manager's state
                    var toggle_launcher_menu = self.toggle_launcher_menu;
                    self.toggle_launcher_menu = function (display) {
                        var action, controller;
                        if (!display) {
                            action = self.action_manager.getCurrentAction();
                            controller = self.action_manager.getCurrentController();
                        }
                        self.current_action_updated(action, controller);
                        toggle_launcher_menu.apply(self, arguments);
                    };
                });
            },
            instanciate_menu_widgets: function () {
                var self = this;
                return this._super.apply(this, arguments).then(function () {
                    // Compatibility with community debug manager
                    self.systray_menu = self.menu.systray_menu;
                });
            },
        });
    }
});
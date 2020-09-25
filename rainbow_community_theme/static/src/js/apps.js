odoo.define('rainbow_community_theme.apps', function (require) {
    "use strict";

    var Apps = require('web.Apps');

    Apps.include({
        // Do nothing on update count as needactions have been removed in enterprise
        _on_update_count: function () {},
    });
});
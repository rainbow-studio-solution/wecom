odoo.define('rainbow_community_theme.system_name', function (require) {
    "use strict";

    var WebClient = require('web.WebClient');
    WebClient.include({
        init: function() {
            this._super.apply(this, arguments);
            this.set('title_part', {"zopenerp": document.title});
        }
    });

});
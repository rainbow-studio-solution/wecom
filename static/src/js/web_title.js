odoo.define('web_title', function (require) {
    "use strict";

    var AbstractWebClient = require('web.AbstractWebClient');

    var WebClient = require('web.WebClient');

    WebClient.include({
        init: function() {
            this._super.apply(this, arguments);
            this.set('title_part', {"zopenerp": document.title});
        }
    });


    // AbstractWebClient.include({
    //     init: function () {
    //         this._super.apply(this, arguments);
    //         this.set('title_part', {"zopenerp": "ERP"});
    //     },
    // });

});
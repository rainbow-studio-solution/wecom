odoo.define('wxwork_auth_oauth.qr_dialog', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    var core = require('web.core');
    var _t = core._t;
    var qweb = core.qweb;

    publicWidget.registry.WxWorkQrDialog = publicWidget.Widget.extend({
        selector: '.o_login_auth',
        xmlDependencies: ['/wxwork_auth_oauth/static/src/xml/dialog.xml'],
        events: {
            'click a': '_pop_up_qr_dialog',
        },
        init: function () {
            this._super.apply(this, arguments);
        },
        _pop_up_qr_dialog: function (ev) {
            ev.preventDefault(); //阻止默认行为
            var self = this;
            var url = $(ev.target).attr('href');
            var icon = $(ev.target).find("i")
            if (icon.hasClass("fa-qrcode")) {
                var dialog = $(qweb.render('wxwork_auth_oauth.QrDialog', {
                    url: url
                }));
                if (self.$el.parents("body").find("#wxwork_qr_dialog").length == 0) {
                    dialog.appendTo($(document.body));
                }
                dialog.modal('show');
            } else {
                window.open(url);
            }
        }
    })
});
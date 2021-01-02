odoo.define('wxwork_auth_oauth.auth', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    var core = require('web.core');
    var _t = core._t;
    var qweb = core.qweb;

    publicWidget.registry.WxWorkAuth = publicWidget.Widget.extend({
        selector: '.o_login_auth',
        xmlDependencies: ['/wxwork_auth_oauth/static/src/xml/auth.xml'],
        events: {
            'click a': '_pop_up_qr_dialog',
        },
        init: function () {
            this._super.apply(this, arguments);
        },
        start: function () {
            var self = this;
            self.is_wxwork_browser();
            return this._super.apply(this, arguments);
        },
        is_wxwork_browser: function () {
            var self = this;
            var ua = navigator.userAgent.toLowerCase();
            let isWx = ua.match(/MicroMessenger/i) == "micromessenger";
            if (!isWx) {
                return false;
            } else {
                var dialog;
                this.isWxworkBrowser = false;
                if (ua.match(/WxWork/i) == "wxwork") {
                    // 检测到是企业微信内置浏览器
                    this.isWxworkBrowser = true;
                    dialog = $(qweb.render('wxwork_auth_oauth.LoginDialog', {
                        isWxworkBrowser: true
                    }));
                    if (self.$el.parents("body").find("#wxwork_login_dialog").length == 0) {
                        dialog.appendTo($(document.body));
                    }
                    dialog.modal('show');

                    var logon_button = dialog.find("button:first");

                    logon_button.click(function (event) {
                        var url = self.$el.find("i.fa-wechat").parent().attr('href');
                        window.open(url);
                    })
                } else {
                    this.isWxworkBrowser = false;
                }
            }
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
            } else if (icon.hasClass("fa-wechat")) {
                var ua = navigator.userAgent.toLowerCase();
                if (ua.match(/WxWork/i) == "wxwork") {
                    window.open(url);
                } else {
                    var dialog = $(qweb.render('wxwork_auth_oauth.LoginDialog', {
                        isWxworkBrowser: self.isWxworkBrowser
                    }));
                    if (self.$el.parents("body").find("#wxwork_login_dialog").length == 0) {
                        dialog.appendTo($(document.body));
                    }
                    dialog.modal('show');
                }
            } else {
                window.open(url);
            }
        }
    })
});
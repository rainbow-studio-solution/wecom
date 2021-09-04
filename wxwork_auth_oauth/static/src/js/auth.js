odoo.define('wxwork_auth_oauth.auth', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    var core = require('web.core');

    var qweb = core.qweb;
    var _lt = core._lt;
    var _t = core._t;

    var WXWORK_BROWSER_MESSAGES = {
        not_wxwork_browser: _t('The current browser is not an enterprise WeChat built-in browser,' + 'so the one-click login function cannot be used.'),
        is_wxwork_browser: _t('Detected in the enterprise WeChat built-in browser to open the page, ' + 'whether to sign in with one click.'),
    };

    publicWidget.registry.WxWorkAuth = publicWidget.Widget.extend({
        selector: '.o_login_auth ',
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
            this.companies = self._rpc({
                route: "/wxowrk_login_qrcode",
                params: {},
            });
            return this._super.apply(this, arguments);
        },
        is_wxwork_browser: function () {
            var self = this;
            var ua = navigator.userAgent.toLowerCase();
            this.msg = "";
            let isWx = ua.match(/MicroMessenger/i) == "micromessenger";
            if (!isWx) {
                this.msg = WXWORK_BROWSER_MESSAGES["not_wxwork_browser"];
                return false;
            } else {
                var dialog;
                this.isWxworkBrowser = false;
                if (ua.match(/WxWork/i) == "wxwork") {
                    // 检测到是企业微信内置浏览器
                    this.isWxworkBrowser = true;
                    this.msg = WXWORK_BROWSER_MESSAGES["is_wxwork_browser"];
                    dialog = $(qweb.render('wxwork_auth_oauth.LoginDialog', {
                        isWxworkBrowser: true,
                        msg: this.msg
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
        _pop_up_qr_dialog: async function (ev) {
            ev.preventDefault(); //阻止默认行为
            var self = this;
            var url = $(ev.target).attr('href');
            var icon = $(ev.target).find("i")
            var msg = "";

            const data = await Promise.resolve(self.companies);
            console.log(data.length);
            var companies = [];
            if (data.length > 1) {
                $.each(data, function (index, element) {
                    var new_url = self.updateUrlParam(url, 'appid', element["appid"]);
                    new_url = self.updateUrlParam(new_url, 'agentid', element["agentid"]);
                    companies.push({
                        "id": element["id"],
                        "name": element["name"],
                        "url": new_url,
                    });
                });
                if (icon.hasClass("wxwork_auth_scancode")) {
                    var dialog = $(qweb.render('wxwork_auth_oauth.QrDialog', {
                        companies: companies,
                    }));
                    if (self.$el.parents("body").find("#wxwork_qr_dialog").length == 0) {
                        dialog.appendTo($(document.body));
                    }
                    dialog.modal('show');

                } else if (icon.hasClass("wxwork_auth_onekey")) {
                    var ua = navigator.userAgent.toLowerCase();
                    if (ua.match(/WxWork/i) == "wxwork") {
                        window.open(url);
                    } else {
                        var dialog = $(qweb.render('wxwork_auth_oauth.LoginDialog', {
                            isWxworkBrowser: self.isWxworkBrowser,
                            msg: this.msg,
                            companies: companies,
                        }));
                        if (self.$el.parents("body").find("#wxwork_login_dialog").length == 0) {
                            dialog.appendTo($(document.body));
                        }
                        dialog.modal('show');
                    }
                }
            } else {
                window.open(url);
            }
        },
        updateUrlParam: function (url, name, new_value) {
            var self = this;

            if (url.indexOf(name + '=') > 0) {
                // url有参数名，进行修改
                var original_value = self.getUrlParam(url, name);
                if (original_value != "") {
                    //url包含参数值
                    url = url.replace(name + '=' + original_value, name + '=' + new_value)
                } else {
                    //url不包含参数值
                    url = url.replace(name + '=', name + '=' + new_value)
                }

            } else {
                // url无参数名，进行添加
                if (url.indexOf("?") > 0) {
                    url = url + "&" + name + "=" + new_value;
                } else {
                    url = url + "?" + name + "=" + new_value;
                }
            }
            return url;
        },
        getUrlParam: function (url, paraName) {
            var arrObj = url.split("?");
            if (arrObj.length > 1) {
                var arrPara = arrObj[1].split("&");
                var arr;
                for (var i = 0; i < arrPara.length; i++) {
                    arr = arrPara[i].split("=");
                    if (arr != null && arr[0] == paraName) {
                        return arr[1];
                    }
                }
                return "";
            } else {
                return "";
            }
        },
    })
});
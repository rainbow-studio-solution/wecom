odoo.define('wxwork_auth_oauth.providers', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var core = require('web.core');
    var qweb = core.qweb;
    var lazyloader = require('web.public.lazyloader');

    publicWidget.registry.WxWorkAuthProviders = publicWidget.Widget.extend({
        selector: '.o_login_auth',
        xmlDependencies: ['/wxwork_auth_oauth/static/src/xml/providers.xml'],
        events: {
            'click a': '_pop_up_qr_dialog',
        },
        init: function () {
            this._super.apply(this, arguments);
        },
        start: function () {
            var self = this;
            this.companies = self._rpc({
                route: "/wxowrk_login_info",
                params: {
                    is_wxwork_browser: self.is_wxwork_browser()
                },
            });

            return this._super.apply(this, arguments);
        },
        is_wxwork_browser: function () {
            var self = this;
            var ua = navigator.userAgent.toLowerCase();
            let isWx = ua.match(/MicroMessenger/i) == "micromessenger";
            if (!isWx) {
                return false;
            } else {
                let isWxWork = ua.match(/WxWork/i) == "wxwork";
                if (isWxWork) {
                    return true;
                } else {
                    return false;
                }
            }
        },
        _pop_up_qr_dialog: async function (ev) {
            ev.preventDefault(); //阻止默认行为
            var self = this;
            var url = $(ev.target).attr('href');
            var icon = $(ev.target).find("i")

            const data = await Promise.resolve(self.companies);

            if ($(ev.target).prop("tagName") == "I") {
                url = $(ev.target).parent().attr('href');
                icon = $(ev.target);
            }

            var companies = [];
            if (data["companies"].length > 1) {
                $.each(data["companies"], function (index, element) {
                    var state = self.getUrlParam(url, "state").replace(/[+]/g, "").replace("#wechat_redirect", "");
                    var state_decode_str = decodeURIComponent(state);
                    var new_state = state_decode_str.slice(0, 1) + '"a":' + '"' + element["appid"] + '",' + state_decode_str.slice(1);
                    var state_encode_str = encodeURIComponent(new_state)

                    var new_url = self.updateUrlParam(url, 'state', state_encode_str);
                    new_url = self.updateUrlParam(new_url, 'appid', element["appid"]);
                    new_url = self.updateUrlParam(new_url, 'agentid', element["agentid"]);

                    new_url = new_url + "#wechat_redirect";

                    companies.push({
                        "id": element["id"],
                        "name": element["name"],
                        "url": new_url,
                    });
                });

                if (icon.hasClass("wxwork_auth_scancode")) {
                    var dialog = $(qweb.render('wxwork_auth_oauth.OauthQrDialog', {
                        companies: companies,
                    }));
                    if (self.$el.parents("body").find("#wxwork_qr_dialog").length == 0) {
                        dialog.appendTo($(document.body));
                    }
                    dialog.modal('show');

                } else if (icon.hasClass("wxwork_auth_onekey")) {


                    var ua = navigator.userAgent.toLowerCase();
                    // if (ua.match(/WxWork/i) == "wxwork") {
                    //     window.open(url);
                    // } else {


                    // }
                    var new_data = {
                        isWxworkBrowser: data["is_wxwork_browser"],
                        msg: data["msg"],
                        companies: companies,
                    };
                    var dialog = $(qweb.render('wxwork_auth_oauth.OauthLoginDialog', {
                        data: new_data
                    }));
                    if (self.$el.parents("body").find("#wxwork_login_dialog").length == 0) {
                        dialog.appendTo($(document.body));
                    }
                    dialog.modal('show');
                } else {
                    window.open(url);
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
odoo.define('wxwork_auth_oauth.providers', function (require) {
    'use strict';

    const publicWidget = require('web.public.widget');
    var core = require('web.core');
    var qweb = core.qweb;


    publicWidget.registry.WxWorkAuthProviders = publicWidget.Widget.extend({
        selector: '.o_login_auth',
        xmlDependencies: ['/wxwork_auth_oauth/static/src/xml/providers.xml'],
        events: {
            'click a': '_pop_up_qr_dialog',
        },

        init: function () {
            this._super.apply(this, arguments);
            window.onerror = function (message, file, line, col, error) {
                alert(message, file, line, col, error)
            }
        },
        start: function () {
            var self = this;
            this.companies = self._rpc({
                route: "/wxowrk_login_info",
                params: {
                    is_wxwork_browser: self.is_wxwork_browser()
                },
            });

            // 判断是 iphone 或者 ipa后，加载WeixinJSBridge，
            if (self.is_ios()) {
                // wx.config({
                //     beta: true, // 必须这么写，否则wx.invoke调用形式的jsapi会有问题
                //     debug: true, // 开启调试模式,调用的所有api的返回值会在客户端alert出来，若要查看传入的参数，可以在pc端打开，参数信息会通过log打出，仅在pc端时才会打印。
                //     appId: '', // 必填，企业微信的corpID
                //     timestamp: '', // 必填，生成签名的时间戳
                //     nonceStr: '', // 必填，生成签名的随机串
                //     signature: '', // 必填，签名，见 附录-JS-SDK使用权限签名算法
                //     jsApiList: [] // 必填，需要使用的JS接口列表，凡是要调用的接口都需要传进来
                // });


                // // WeixinJSBridge.invoke('hideOptionMenu');
                // if (typeof WeixinJSBridge == "undefined") { //屏蔽分享按钮
                //     if (document.addEventListener) {
                //         document.addEventListener('WeixinJSBridgeReady', onBridgeReady, false);
                //     } else if (document.attachEvent) {
                //         document.attachEvent('WeixinJSBridgeReady', onBridgeReady);
                //         document.attachEvent('onWeixinJSBridgeReady', onBridgeReady);
                //     }
                // } else {
                //     onBridgeReady();
                // }

                // function onBridgeReady() { //隐藏右上角按钮
                //     WeixinJSBridge.call('hideOptionMenu');
                // }
            }


            return this._super.apply(this, arguments);
        },
        is_wxwork_browser: function () {
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
        is_ios: function () {
            var isIphoneOrIpad = /iphone|ipad/i.test(navigator.userAgent);
            if (isIphoneOrIpad) {
                return true;
            } else {
                return false;
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
            if (data["companies"].length > 0) {
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
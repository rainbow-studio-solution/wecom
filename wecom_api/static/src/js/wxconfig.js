odoo.define('wecom_client_api.wxconfig', function (require) {
    "use strict";
    var Widget = require('web.Widget');

    var Wxconfig = Widget.extend({
        init: function (parent, options) {
            var self = this;
            this._super(parent);
            console.log(parent)
            options = _.defaults(options || {}, {
                beta: true, // 必须这么写，否则wx.invoke调用形式的jsapi会有问题
                debug: true, // 开启调试模式,调用的所有api的返回值会在客户端alert出来，若要查看传入的参数，可以在pc端打开，参数信息会通过log打出，仅在pc端时才会打印。
                appId: '', // 必填，企业微信的corpID
                timestamp: '', // 必填，生成签名的时间戳
                nonceStr: '', // 必填，生成签名的随机串
                signature: '', // 必填，签名，见 附录-JS-SDK使用权限签名算法
                jsApiList: [] // 必填，需要使用的JS接口列表，凡是要调用的接口都需要传进来
            });
            this.beta = options.beta;
            this.debug = options.debug;
            this.appId = options.appId;
            this.timestamp = options.timestamp;
            this.nonceStr = options.nonceStr;
            this.signature = options.signature;
            this.jsApiList = options.jsApiList;

            // self.debug_alert("init:" + this.jsApiList);
        },
        debug_alert: function (msg) {
            window.alert(msg);
            console.log(msg)
        },
        start: function () {
            /*
             * 通过config接口注入权限验证配置
             * 调用wx.agentConfig之前，必须确保先成功调用wx.config. 
             */
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                // self.debug_alert("debug:" + self.debug);
                wx.config({
                    beta: self.beta,
                    debug: self.debug,
                    appId: self.appId,
                    timestamp: self.timestamp,
                    nonceStr: self.nonceStr,
                    signature: self.signature,
                    jsApiList: self.jsApiList
                });
            });
        },
        ready: function () {
            var self = this;
            wx.ready({
                // config信息验证后会执行ready方法，所有接口调用都必须在config接口获得结果之后，config是一个客户端的异步操作，所以如果需要在页面加载时就调用相关接口，则须把相关接口放在ready函数中调用来确保正确执行。对于用户触发时才调用的接口，则可以直接调用，不需要放在ready函数中。
            });
            return this;
        },
        error: function (res) {
            var self = this;
            wx.error(function (res) {
                // config信息验证后会执行ready方法，所有接口调用都必须在config接口获得结果之后，config是一个客户端的异步操作，所以如果需要在页面加载时就调用相关接口，则须把相关接口放在ready函数中调用来确保正确执行。对于用户触发时才调用的接口，则可以直接调用，不需要放在ready函数中。
                console.log(res)
            });
            return this;
        }
    });
    return Wxconfig;
});
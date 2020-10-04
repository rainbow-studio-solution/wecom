odoo.define('wxwrok.wx_config', function (require) {
    "use strict";
    var Widget = require('web.Widget');

    var Wxconfig = Widget.extend({
        init: function (parent, options) {
            var self = this;
            this._super(parent);
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
            // this.jsApiList = options.jsApiList;
            this.jsApiList = ['chooseImage'];
            console.log(this.jsApiList);
        },
        start: function () {
            /*
             * 通过config接口注入权限验证配置
             * 调用wx.agentConfig之前，必须确保先成功调用wx.config. 
             */
            wx.config({
                beta: this.beta,
                debug: this.debug,
                appId: this.appId,
                timestamp: this.timestamp,
                nonceStr: this.nonceStr,
                signature: this.signature,
                jsApiList: this.jsApiList
            });
            wx.ready(function () {
                wx.checkJsApi({
                    jsApiList: ["invoke", "scanQRCode"], // 需要检测的JS接口列表，所有JS接口列表见附录2,
                    success: function (res) {
                        console.log("jsApiList", res)
                        // 以键值对的形式返回，可用的api值true，不可用为false
                        // 如：{"checkResult":{"chooseImage":true},"errMsg":"checkJsApi:ok"}
                    }
                });
            });
            wx.error(function (res) {
                // config信息验证失败会执行error函数，如签名过期导致验证失败，具体错误信息可以打开config的debug模式查看，也可以在返回的res参数中查看，对于SPA可以在这里更新签名。
                console.log("错误：" + JSON.stringify(res));
            });
        },
        error: function () {
            // return Promise.resolve(this.configStatus)
            // return this.configStatus;
        }
    });
    return Wxconfig;
});
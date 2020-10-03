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
            this.jsApiList = options.jsApiList;
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
                // config信息验证后会执行ready方法，所有接口调用都必须在config接口获得结果之后，config是一个客户端的异步操作，所以如果需要在页面加载时就调用相关接口，则须把相关接口放在ready函数中调用来确保正确执行。对于用户触发时才调用的接口，则可以直接调用，不需要放在ready函数中。
                wx.checkJsApi({
                    jsApiList: ['chooseImage'], // 需要检测的JS接口列表，所有JS接口列表见附录2,
                    success: function (res) {
                        // 以键值对的形式返回，可用的api值true，不可用为false
                        // 如：{"checkResult":{"chooseImage":true},"errMsg":"checkJsApi:ok"}
                        console.log("success:", res);
                    }
                });
                wx.scanQRCode({
                    desc: 'scanQRCode desc',
                    needResult: 1, // 默认为0，扫描结果由企业微信处理，1则直接返回扫描结果，
                    scanType: ["qrCode", "barCode"], // 可以指定扫二维码还是条形码（一维码），默认二者都有
                    success: function (res) {
                        console.log("scanQRCode:", res);
                    },
                    error: function (res) {
                        if (res.errMsg.indexOf('function_not_exist') > 0) {
                            alert('版本过低请升级')
                        }
                    }
                });
            });
            wx.error(function (res) {
                // config信息验证失败会执行error函数，如签名过期导致验证失败，具体错误信息可以打开config的debug模式查看，也可以在返回的res参数中查看，对于SPA可以在这里更新签名。
                console.log("error:", res);
            });
        }

    });
    return Wxconfig;
});
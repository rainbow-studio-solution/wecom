odoo.define('web.wxwrok_scan_widget', function (require) {
    "use strict";

    var core = require('web.core');
    var utils = require('web.utils')
    var config = require('web.config');
    var fieldRegistry = require('web.field_registry');
    var FieldChar = require('web.basic_fields').FieldChar;
    var Dialog = require('web.Dialog');

    var _t = core._t;

    var QWeb = core.qweb;
    var WEB_CAMERA_SCANCODE_WIDGET_COOKIE = 'web_camera_scan_code_widget_default_camera';

    function Q(el) {
        if (typeof el === "string") {
            var els = document.querySelectorAll(el);
            return typeof els === "undefined" ? undefined : els.length > 1 ? els : els[0];
        }
        return el;
    }

    var WxworkScan = FieldChar.extend({
        template: 'WxworkScan',
        className: 'o_field_wxwrok_scan',
        cssLibs: [

        ],
        jsLibs: [
            'http://res.wx.qq.com/open/js/jweixin-1.2.0.js'
        ],


        init: function (parent) {
            this._super.apply(this, arguments);

        },

        initWebScanner: function () {
            var self = this;
            var header_button = this.dialog.$modal.find("header").find("button");
            header_button.click(function () {
                self.disableWebCamera();
            });

            // var show_or_hide_options_button = this.dialog.$modal.find(".modal-body").find(".show_or_hide_options_panel");
            // show_or_hide_options_button.click(function () {
            //     self.show_or_hide_options_container();
            // });

            // this.dialog.$modal.find(".modal-body").find("input[type='checkbox']").bootstrapSwitch("size", "mini");
            // this.scannerLaser = this.dialog.$modal.find(".modal-body").find(".scanner-laser");
            // this.scan_result_format = this.dialog.$modal.find(".modal-body").find(".scan_result_format");
            // this.scan_result_value = this.dialog.$modal.find(".modal-body").find(".scan_result_value");

            var sacn_options = {

            };

            // this.decoder = new WebCodeCamJS("#webcodecam-canvas").buildSelectMenu("#camera-select", "environment|back").init(sacn_options);
            // this.decoder.play();
            // this.scan_result_format.val(_t("Scanning...")).addClass("text-info").removeClass("text-danger").removeClass("text-success");;
        },
        isEnterprise: function () {
            // 判断是否企业版
            var isEnterprise = _.last(odoo.session_info.server_version_info) === 'e';
            return isEnterprise
        },
        open_dialog: function () {
            var self = this;
            if (!self.isEnterprise()) {
                self.open_scan_dialog();
            } else {

            }
        },
        open_scan_dialog: function () {
            var self = this;
            this.$input.find("button[class*='show_scan_code_camera']").prop('disabled', true); //禁用 --变灰，且不能调用点击事件
            this.$input.find(".loading").removeClass("o_hidden")

            var dialog_title = _t("Enterprise WeChat Scan Code");
            this.dialog = new Dialog(this, {
                size: 'medium',
                dialogClass: 'o_act_window',
                title: dialog_title,
                buttons: self.getWebButtons(),
                $content: QWeb.render('WxworkScan.camera', {
                    // cameras: res.data,
                    // active: this.activeCameraId,
                    // error: res.msg,
                })
            });
            this.dialog.opened().then(function () {
                var timestamp = new Date().getTime();
                var nonceStr = self.generateNonceStr(16);
                //通过config接口注入权限验证配置
                wx.config({
                    beta: true, // 必须这么写，否则wx.invoke调用形式的jsapi会有问题
                    debug: self.get_config_parameter("wxwork.debug_enabled"), // 开启调试模式,调用的所有api的返回值会在客户端alert出来，若要查看传入的参数，可以在pc端打开，参数信息会通过log打出，仅在pc端时才会打印。
                    appId: self.get_config_parameter("wxwork.wxwork.auth_agentid"), // 必填，企业微信的corpID
                    timestamp: timestamp, // 必填，生成签名的时间戳
                    nonceStr: nonceStr, // 必填，生成签名的随机串
                    signature: '', // 必填，签名，见 附录-JS-SDK使用权限签名算法
                    jsApiList: [] // 必填，需要使用的JS接口列表，凡是要调用的接口都需要传进来
                });

                self.initWebScanner();
            });
            this.dialog.open();
        },
        generateSignature: function () {
            //生成签名

        },
        generateNonceStr: function (len) {
            //生成签名的随机串
            len = len || 32;
            var $chars = 'ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678'; // 默认去掉了容易混淆的字符oOLl,9gq,Vv,Uu,I1
            var maxPos = $chars.length;
            var str = '';
            for (i = 0; i < len; i++) {
                str += $chars.charAt(Math.floor(Math.random() * maxPos));
            }
            return str;
        },
        get_config_parameter: function (parameter) {
            var self = this;
            self._rpc({
                model: 'ir.config_parameter',
                method: 'get_param',
                args: [parameter],
                lazy: false,
            }).then(function (response) {
                console.log(response);
                return response;
            })
        },
        show_or_hide_options_container: function () {
            var camera_options_container = this.dialog.$modal.find(".modal-body").find(".o_camera_widget_options");
            var icon = this.dialog.$modal.find(".modal-body").find(".show_or_hide_options_panel").find("i");
            var span = this.dialog.$modal.find(".modal-body").find(".show_or_hide_options_panel").find("span");

            if (camera_options_container.hasClass('o_hidden')) {
                icon.addClass("fa-angle-double-up").removeClass("fa-angle-double-down");
                camera_options_container.removeClass("o_hidden");
                span.html(_t("Hide"));
            } else {
                icon.addClass("fa-angle-double-down").removeClass("fa-angle-double-up");
                camera_options_container.addClass("o_hidden");
                span.html(_t("Show"));
            }
        },
        disableWebCamera: function () {
            var self = this;
            // this.decoder.stop();
            this.$input.find(".loading").addClass("o_hidden");
            this.$input.find("button[class*='show_scan_code_camera']").prop('disabled', false); //启用

        },
        getWebButtons: function () {
            var self = this;
            var buttons = [];
            if (this.nodeOptions.confirm !== false || this.nodeOptions.confirm === "" || this.nodeOptions.confirm === undefined) {
                buttons = [{
                    text: _t("Confirm"),
                    classes: 'btn-primary',
                    close: false,
                    click: function () {
                        if (self.scanResult === null) {
                            this.$modal.find("input").removeClass("bg-success").addClass(
                                "bg-warning");
                            this.$modal.find("input").val(_t(
                                "Scan has not been performed, please scan."))
                        } else {
                            this.$modal.find("input").removeClass("bg-warning").addClass(
                                "bg-success");
                        }
                    }
                }, {
                    text: _t("Cancel"),
                    classes: 'btn-default',
                    close: true,
                    click: function () {
                        self.disableWebCamera();
                    }
                }];
            } else if (!this.nodeOptions.confirm) {
                buttons = [{
                    text: _t("Cancel"),
                    classes: 'btn-default',
                    close: true,
                    click: function () {
                        self.disableWebCamera();
                    }
                }]
            }
            return buttons;
        },
        /*

        */
        _renderEdit: function () {
            var $input = this.$el.find('input');
            this.$loading = this.$el.find('.loading');

            if (this.value === null || this.value === "" || this.value === false) {
                return this._super($input.val(""));
            } else {
                return this._super($input.val(this.value));
            }
        },
        _prepareInput: function ($input) {
            var self = this;
            var button = $input.find("button[class*='show_scan_code_camera']")

            button.click(function () {
                self.open_dialog();
            })

            return $.when($input, this._super.apply(this, arguments));
        },
        _setValue: function () {
            var $input = this.$el.find('input');
            return this._super($input.val());
        },
    });

    fieldRegistry.add('wxwork_scan', WxworkScan);
    return {
        WxworkScan: WxworkScan
    };
});
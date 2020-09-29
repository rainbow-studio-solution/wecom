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

            var show_or_hide_options_button = this.dialog.$modal.find(".modal-body").find(".show_or_hide_options_panel");
            show_or_hide_options_button.click(function () {
                self.show_or_hide_options_container();
            });

            this.dialog.$modal.find(".modal-body").find("input[type='checkbox']").bootstrapSwitch("size", "mini");
            this.scannerLaser = this.dialog.$modal.find(".modal-body").find(".scanner-laser");
            this.scan_result_format = this.dialog.$modal.find(".modal-body").find(".scan_result_format");
            this.scan_result_value = this.dialog.$modal.find(".modal-body").find(".scan_result_value");

            var sacn_options = {
                autoBrightnessValue: 100,
                resultFunction: function (res) {
                    self.scannerLaser.fadeOut(0.5);
                    setTimeout(function () {
                        self.scannerLaser.fadeIn(0.5);
                    });
                    self.scan_result_format.val(_t("Type") + ": " + res.format).addClass("text-success").removeClass("text-danger").removeClass("text-info");
                    self.scan_result_value.val(res.code).addClass("text-success");
                },
                getDevicesError: function (error) {
                    var p, message = "Error detected with the following parameters:\n";
                    for (p in error) {
                        message += p + ": " + error[p] + "\n";
                    }
                    // alert(message);
                    self.scan_result_format.val(_t("Error") + ":" + error.name).addClass("text-danger");
                    self.scan_result_value.val(message).addClass("text-danger");
                },
                getUserMediaError: function (error) {
                    var p, message = "Error detected with the following parameters:\n";
                    for (p in error) {
                        message += p + ": " + error[p] + "\n";
                    }
                    // alert(message);

                    self.scan_result_format.val(_t("Error") + ":" + error.name).addClass("text-danger");
                    self.scan_result_value.val(message).addClass("text-danger");
                },
                cameraError: function (error) {
                    var p, message = "Error detected with the following parameters:\n";
                    if (error.name == "NotSupportedError") {
                        var ans = confirm("Your browser does not support getUserMedia via HTTP!\n(see: https:goo.gl/Y0ZkNV).\n You want to see github demo page in a new window?");
                        if (ans) {
                            window.open("https://andrastoth.github.io/webcodecamjs/");
                        }
                    } else {
                        for (p in error) {
                            message += p + ": " + error[p] + "\n";
                        }

                        self.scan_result_format.val(_t("Error") + ":" + error.name).addClass("text-danger");
                        self.scan_result_value.val(message).addClass("text-danger");
                    }
                },
                cameraSuccess: function () {
                    // grabImg.classList.remove("disabled");
                }
            };

            this.decoder = new WebCodeCamJS("#webcodecam-canvas").buildSelectMenu("#camera-select", "environment|back").init(sacn_options);
            this.decoder.play();
            this.scan_result_format.val(_t("Scanning...")).addClass("text-info").removeClass("text-danger").removeClass("text-success");;
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

            var dialog_title = _t("QR code and Bar code Scanning");
            this.dialog = new Dialog(this, {
                size: 'medium',
                dialogClass: 'o_act_window',
                title: dialog_title,
                buttons: self.getWebButtons(),
                $content: QWeb.render('ScanCode.camera', {
                    // cameras: res.data,
                    // active: this.activeCameraId,
                    // error: res.msg,
                })
            });
            this.dialog.opened().then(function () {
                // self.initWebScanner(dialog, res.data);
                self.initWebScanner();
            });
            this.dialog.open();
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
            this.decoder.stop();
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
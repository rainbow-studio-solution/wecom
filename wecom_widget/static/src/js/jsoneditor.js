odoo.define("wecom.FieldTextJson", function (require) {
    'use strict';
    var basic_fields = require('web.basic_fields');
    var dom = require('web.dom');
    var field_registry = require('web.field_registry');
    var core = require('web.core');
    var _lt = core._lt;
    var _t = core._t;

    var FieldTextJson = basic_fields.FieldText.extend({
        description: _lt("Json Editor"),
        // template: "JsonEditor",
        className: [
            basic_fields.FieldText.prototype.className,
            'o_form_field_jsoneditor',
        ].join(' '),
        tagName: 'div',
        jsLibs: [
            '/wecom_widget/static/lib/jsoneditor/js/jsoneditor.js',
        ],
        cssLibs: [
            '/wecom_widget/static/lib/jsoneditor/jsoneditor.css',
        ],
        init: function () {
            var self = this;
            this._super.apply(this, arguments);
            if (this.mode === 'edit') {
                this.tagName = 'div';
            }
            //暗色主题，默认为true
            this.darktheme = self.convertBoolean(self.nodeOptions.darktheme);
            if (this.darktheme) {
                this.cssLibs.push('/wecom_widget/static/lib/jsoneditor/css/darktheme.css');
            }
            this.modes = self.get_modes(self.nodeOptions.modes);
            this.isJSON = true;
        },
        start: function () {
            var self = this;
            self.$error_el = $("<div class='alert mb-2'></div>");
            this._super.apply(this, arguments).then(function () {
                self.$el.parent().prepend(self.$error_el);
            });
        },

        _prepareInput: function () {
            var $input = this._super.apply(this, arguments);
            var self = this;
            self.json_data = $input.val();
            $input.empty();
            _.defer(function ($elm) {
                if (this.mode === 'edit' && $input.length > 1) {
                    $.each($input, function (index, e) {
                        if (index > 0) {
                            // $(e).remove();
                            $(e).addClass("d-none");
                        }
                    })
                }

                $input.removeClass(this.className);
                $input.wrap(_.str.sprintf("<div class='%s'></div>", self.className));
                $elm.removeAttr("style");

                self.$editor = new JSONEditor($elm.get(0), self._getJsonEditorOptions());

                //添加翻译按钮 mode : "readonly" "edit"
                if (this.res_id && this.mode == "edit") {
                    if (_t.database.multi_lang && this.field.translate) {
                        var $translate = this._renderTranslateButton();
                        $translate.addClass("jsoneditor-translate fa fa-language fa-lg");
                        self.$editor.menu.appendChild($translate[0]);
                        // self.$editor.dom.translate = $translate[0];
                    }

                }
                if ($input.val() != "") {
                    self.$editor.set(jQuery.parseJSON($input.val()));
                }
            }.bind(this), $input);

            // console.log(self.$el.parent().find(".o_form_field_jsoneditor").length)
            return $input;
        },
        _renderReadonly: function () {
            this._prepareInput(this.$el);
        },
        _renderEdit: function () {
            this._prepareInput(this.$el);
        },
        _setValue: function () {
            var self = this;
            if (!self.isJSON) {
                // json 不合法 弹出通知
                var title = _t('Json Validation Error');
                var message = _t("Please check the JSON text!");
                var className = "";
                return self.do_warn_notify(title, message, className);
            } else {
                return this._super(self.json_data);
            }
        },
        // --------------------------------------------------------------------------
        // Json编辑器
        // --------------------------------------------------------------------------
        get_modes: function (value) {
            var self = this;
            if (self.isEmptyObject(value)) {
                //空字典
                return ['text', 'code', 'tree', 'form', 'view', 'preview'];
            } else {
                //非空字典
                if ($.inArray("code", value) == -1) {
                    value.push("code");
                }
                return value;
            }
        },
        isEmptyObject: function (obj) {
            for (var key in obj) {
                return false;
            }
            return true;
        },
        convertBoolean: function (value) {
            switch (value) {
                case false:
                    return false;
                    break;
                case undefined:
                    return true;
                    break;
                case null:
                    return true;
                    break;
                case 0:
                    return false;
                    break;
                case -0:
                    return false;
                    break;
                case NaN:
                    return true;
                    break;
                case "":
                    return true;
                    break;
                default:
                    return true;
            }
        },

        _getJsonEditorOptions: function () {
            var self = this;
            var error_text = _t('Json Validation Error');
            var correct_tips = _t("Json validation is correct. Can be saved");
            var options = {
                mode: 'code',
                ace: ace,
                onChangeText: function (jsonString) {
                    if (jsonString == "") {
                        self.json_data = "";
                        self._setValue();
                    }
                },
                onValidationError: function (errors) {
                    // 检验json合法
                    var error_str = "<code>" + error_text + "</code> " + "<code>" + _t(" ,Can't save") + "</code> " + " <br> " +
                        _t("was called with ") + errors.length + _t(" error") +
                        (errors.length > 1 ? 's' : '') + " <br> " +
                        _t("open the browser console to see the error objects");
                    self.$error_el.html(error_str).addClass("alert-warning").removeClass("alert-success");
                    self.isJSON = false;
                    if (self.mode === "edit") {
                        console.error(error_text, errors);
                    }

                    if (errors.length == 0) {
                        self.isJSON = true;
                        self.$error_el.html("<code>" + correct_tips + "<code>").addClass("alert-success").removeClass("alert-warning");
                    }
                },
                onValidate: function (json) {
                    // 验证json合法
                    self.isJSON = true;

                    if (self.mode === "edit") {
                        self.json_data = JSON.stringify(json);
                        self._setValue();
                    }

                    self.$error_el.html("<code>" + correct_tips + "<code>").addClass("alert-success").removeClass("alert-warning");
                }
            };
            if (self.mode === "readonly") {
                options["renderMode"] = _t("Read-only mode");
                options["modes"] = ['text', 'code', 'preview'];
                options["onEditable"] = function (node) {
                    if (!node.path) {
                        // 只读模式
                        return false;
                    }
                };
                self.$error_el.hide();
            } else if (self.mode === "edit") {
                options["renderMode"] = _t("Edit mode");
                options["modes"] = self.modes;
                self.$error_el.show();
            }
            return options;
        },

        do_warn_notify: function (title, message, className) {
            var self = this;
            self.displayNotification({
                type: 'warning',
                title: title,
                message: message,
                sticky: false,
                className: className,
            });
            return Promise.reject();
        },
    })

    field_registry.add('wecom_jsoneditor', FieldTextJson);
    return FieldTextJson;
});
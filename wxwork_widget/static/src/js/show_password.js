odoo.define("wxwork_widget.ShowPasswordFieldText", function (require) {
    'use strict';

    var core = require('web.core');
    var qweb = core.qweb;
    var _t = core._t;
    var _lt = core._lt;

    var FieldChar = require('web.basic_fields').FieldChar;

    var fieldRegistry = require('web.field_registry');


    var ShowPasswordFieldText = FieldChar.extend({
        description: _lt("Show Password"),
        template: 'ShowPasswordInput',
        ShowPasswordTemplate: 'ShowPasswordButton',
        className: 'o_field_showpassword',
        init: function (parent) {
            this._super.apply(this, arguments);
        },
        _renderReadonly: function () {
            this._super.apply(this, arguments);
            var self = this;
            var $button = $(qweb.render(this.ShowPasswordTemplate));
            if (this.value) {
                this.$el.text(new Array(this.value.trim().length).join('●')).data("state", "hide");
                this.$el = this.$el.append($button);
                $button.mousedown(function (ev) {
                    self._showSpanPassword(ev);
                })
            }
        },
        _showSpanPassword: function (ev) {
            var self = this;
            $(ev.currentTarget).find("span.fa").toggleClass('fa-eye-slash fa-eye');
            var $button = this.$el.find("button.o_show_password_button");
            if (this.$el.data("state") === "hide") {
                this.$el.data("state", "show");
                this.$el.text(this.value)
            } else {
                this.$el.data("state", "hide");
                this.$el.text(new Array(this.value.trim().length).join('●'))
            }
            this.$el = this.$el.append($button);
            $button.mousedown(function (ev) {
                self._showSpanPassword(ev);
            })
        },
        _renderEdit: function () {
            var $input = this.$el.find('input');
            if (this.value) {
                return this._super($input.val(this.value));
            }
        },
        _showInputPassword: function (ev) {
            var $input = this.$el.find('input');
            $input.prop("type",
                (i, old) => {
                    return old === "text" ? "password" : "text";
                }
            );
            $(ev.currentTarget).find("span.fa").toggleClass('fa-eye-slash fa-eye');
        },
        _prepareInput: function ($input) {
            var self = this;
            this.$input = this.$el.find('input');
            var $button = this.$el.find("button.o_show_password_button");

            $button.mousedown(function (ev) {
                self._showInputPassword(ev);
            })
            return $.when($input, this._super.apply(this, arguments));
        },
        _setValue: function () {
            var $input = this.$el.find('input');
            return this._super($input.val());
        },
    });

    fieldRegistry.add('wxwork_password', ShowPasswordFieldText);
    return ShowPasswordFieldText;
});
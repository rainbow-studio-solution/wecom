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
                this.$el.text(new Array(this.value.trim().length + 1).join('●'));

                var $span = this.$el;
                $span.data("state", "hide");
                var new_el = $span[0].outerHTML + $button[0].outerHTML;
                this.$el = $(new_el);

                setTimeout(function () {
                    if (self.$el.parent().length > 0) {
                        self.$el.parent().css({
                            "display": "flex",
                            "flex-wrap": "nowrap",
                            "align-items": "flex-start"
                        });
                        return;
                    }
                }, 500);

                var button = self.$el[1];
                $(button).mousedown(function (ev) {
                    self._showSpanPassword(ev);
                })
            }
        },
        _showSpanPassword: function (ev) {
            var self = this;
            var span = self.$el[0];
            if (typeof ($(span).attr("disguising-password")) != "undefined") {
                $(ev.currentTarget).find("i.fa").addClass('fa-eye').removeClass("fa-eye-slash");
                $(span).data("state", "show");
                $(span).removeAttr("disguising-password");
                $(span).text(this.value)
            } else {
                $(ev.currentTarget).find("i.fa").removeClass('fa-eye').addClass("fa-eye-slash");
                $(span).data("state", "hide");
                $(span).attr("disguising-password", "");
            }
        },
        _renderEdit: function () {
            var $input = this.$el.find('input');
            if (this.value) {
                return this._super($input.val(this.value));
            }
        },
        _showInputPassword: function (ev) {
            var $input = this.$el.find('input');
            if (typeof ($input.attr("disguising-password")) == "undefined") {

                $input.attr("disguising-password", "");
            } else {

                $input.removeAttr("disguising-password");
            }

            $(ev.currentTarget).find("i.fa").toggleClass('fa-eye-slash fa-eye');
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
        _getValue: function () {
            return this.value;
        },
        _onInput: function () {
            var $input = this.$el.find('input');
            this.isDirty = !this._isLastSetValue($input.val());
            // this._doDebouncedAction();
        }
    });

    fieldRegistry.add('wxwork_password', ShowPasswordFieldText);
    return ShowPasswordFieldText;
});
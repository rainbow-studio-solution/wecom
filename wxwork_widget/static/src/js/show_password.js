odoo.define("wxwork_widget.ShowPasswordFieldText", function (require) {
    'use strict';

    var FieldChar = require('web.basic_fields').FieldChar;
    var fieldRegistry = require('web.field_registry');

    var ShowPasswordFieldText = FieldChar.extend({
        template: 'ShowPassword',
        className: 'o_field_showpassword',
        init: function (parent) {
            this._super.apply(this, arguments);
        },
        _renderEdit: function () {
            var $input = this.$el.find('input');
            if (this.value === null || this.value === "" || this.value === false) {
                return this._super($input.val(""));
            } else {
                return this._super($input.val(this.value));
            }
        },
        _prepareInput: function ($input) {
            var self = this;
            this.$input = this.$el.find('input');
            var button = self.$el.find("span.wxwork_show_password");
            button.mousedown(function (ev) {
                self._showPassword(ev);
            })
            return $.when($input, this._super.apply(this, arguments));
        },
        _showPassword: function (ev) {
            $(ev.target).closest('.input-group').find('.form-control').prop("type",
                (i, old) => {
                    return old === "text" ? "password" : "text";
                }
            );
            $(ev.currentTarget).toggleClass('fa-eye-slash fa-eye');
        },
        _setValue: function () {
            var $input = this.$el.find('input');

            return this._super($input.val());
        },
    });

    fieldRegistry.add('wxwork_password', ShowPasswordFieldText);
    return ShowPasswordFieldText;
});
odoo.define("wxwork_widget.PasswordFieldText", function (require) {
    'use strict';
    var fieldRegistry = require('web.field_registry');
    var FieldChar = require('web.basic_fields').FieldChar;
    var core = require('web.core');
    var _lt = core._lt;


    var PasswordFieldText = FieldChar.extend({
        template: 'ShowPassword',
        description: _lt("ShowPassword"),
        className: 'o_form_field_showpassword',
        events: {
            'mousedown span.wxwork_show_password': '_showPassword',
        },
        init: function (parent) {
            var self = this;
            this._super.apply(this, arguments);
        },
        _showPassword: function (ev) {
            $(ev.target).closest('.input-group').find('.form-control').prop("type",
                (i, old) => {
                    return old === "text" ? "password" : "text";
                }
            );
        },
        _renderEdit: function () {
            var $input = this.$el.find('input');
            if (this.value === null || this.value === "" || this.value === false) {
                return this._super($input.val(""));
            } else {
                return this._super($input.val(this.value));
            }
        },

        _setValue: function () {
            var $input = this.$el.find('input');
            return this._super($input.val());
        },
    });

    fieldRegistry.add('wxwork_password', PasswordFieldText);
    return PasswordFieldText;
});
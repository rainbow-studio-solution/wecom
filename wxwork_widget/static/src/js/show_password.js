odoo.define("wxwork_widget.ShowPasswordFieldText", function (require) {
    'use strict';

    // 参考addons\auth_password_policy\static\src\js\password_field.js

    var fields = require('web.basic_fields');
    var fieldRegistry = require('web.field_registry');

    var core = require('web.core');
    var _lt = core._lt;


    var ShowPasswordFieldText = fields.InputField.extend({
        template: 'ShowPassword',
        description: _lt("ShowPassword"),
        className: 'o_form_field_showpassword',
        events: {
            'mousedown span.wxwork_show_password': '_showPassword',
        },
        init: function (parent) {
            this._super.apply(this, arguments);
            this.nodeOptions.isPassword = true;

        },
        _showPassword: function (ev) {
            $(ev.target).closest('.input-group').find('.form-control').prop("type",
                (i, old) => {
                    return old === "text" ? "password" : "text";
                }
            );
        },
        _renderEdit: function () {
            // this.old_password = 
            var $input = this.$el.find('input');
            if (this.value === null || this.value === "" || this.value === false) {
                return this._super($input.val(""));
            } else {
                return this._super($input.val(this.value));
            }
        },
        _onInput: function () {
            this._super();
            this.update(this._getValue());
        }
    });

    fieldRegistry.add('wxwork_password', ShowPasswordFieldText);
    return ShowPasswordFieldText;
});
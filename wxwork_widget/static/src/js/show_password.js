odoo.define("wxwork_widget.ShowPasswordFieldText", function (require) {
    'use strict';

    // 参考addons\auth_password_policy\static\src\js\password_field.js

    var InputField = require('web.basic_fields').InputField;
    var fieldRegistry = require('web.field_registry');

    var core = require('web.core');
    var _lt = core._lt;


    var ShowPasswordFieldText = InputField.extend({
        template: 'ShowPassword',
        description: _lt("ShowPassword"),
        className: 'o_form_field_showpassword',
        events: {
            'mousedown span.wxwork_show_password': '_showPassword',
        },
        init: function (parent) {
            this._super.apply(this, arguments);
            // this.$input = this.$el.find('input');

            console.log("init", this.value);
            // console.log("init", this.$input.val());
        },
        start: function () {
            this.$input = this.$el.find('input');

            console.log("start", this.value);
            console.log("start", this.$input.val());

            return this._super.apply(this, arguments);
        },
        _showPassword: function (ev) {
            $(ev.target).closest('.input-group').find('.form-control').prop("type",
                (i, old) => {
                    return old === "text" ? "password" : "text";
                }
            );
            $(ev.currentTarget).toggleClass('fa-eye-slash fa-eye');
        },
        _renderEdit: function () {
            this.$input = this.$el.find('input');
            console.log("_renderEdit", this.value);
            console.log("_renderEdit", this.$input.val());

            // var $input = this.$el.find('input');
            if (this.value === null || this.value === "" || this.value === false) {
                // return this._super($input.val(""));
                return this._super(this.$input.val(""));
            } else {
                // return this._super($input.val(this.value));
                return this._super(this.$input.val(this.value));
            }
        },
        _prepareInput: function ($input) {
            var self = this;
            return $.when($input, this._super.apply(this, arguments));
        },
        _setValue: function () {
            var $input = this.$el.find('input');
            return this._super($input.val());
        },
        _getValue: function () {
            console.log("_getValue", this.value);
            console.log("_getValue", this.$input.val());

            return this.$input.val();
        },

    });

    fieldRegistry.add('wxwork_password', ShowPasswordFieldText);
    return ShowPasswordFieldText;
});
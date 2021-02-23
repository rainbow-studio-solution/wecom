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
            var $button = $(qweb.render(this.ShowPasswordTemplate))
            if (this.value) {
                this.$el.text(new Array(this.value.trim().length).join('●')).data("state", "hide");
                this.$el = this.$el.append($button);
            }
        },

        _renderEdit: function () {
            var $input = this.$el.find('input');
            if (this.value) {
                return this._super($input.val(this.value));
            }
        },
        _prepareInput: function ($input) {
            this.$input = this.$el.find('input');
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
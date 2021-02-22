odoo.define("wxwork_widget.ShowPasswordFieldText", function (require) {
    'use strict';

    var core = require('web.core');
    var qweb = core.qweb;
    var FieldChar = require('web.basic_fields').FieldChar;
    var fieldRegistry = require('web.field_registry');

    // var ShowPassword = {
    //     _format_password: function () {
    //         var self = this;
    //         var $showBtn = this.$('.o_show_password_button');
    //         var $span = this.$el.find('span');
    //         $span.text(new Array(self.value.trim().length).join('*'));
    //         // console.log(self.value.trim().length);
    //     },
    //     _renderReadonly: function () {
    //         this._super.apply(this, arguments);
    //         if (this.value) {
    //             this.$el.append($(qweb.render(this.showPasswordTemplate)));
    //             this._format_password();
    //         }
    //     },
    //     _renderEdit: function () {
    //         var def = this._super.apply(this, arguments);
    //         var $input = this.$el.find('input');
    //         console.log($input)
    //         if (this.value) {
    //             $input.after($(qweb.render(this.showPasswordTemplate)));
    //             // $input.insertAfter($(qweb.render(this.showPasswordTemplate)));
    //             // $(qweb.render(this.showPasswordTemplate)).insertAfter($input);
    //         }
    //         return def;
    //     },

    // }

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
        _renderReadonly: function () {
            this._super.apply(this, arguments);
            var self = this;
            var $span = $('<button class = "btn btn-sm btn-primary o_show_password_button"><span class="fa fa-eye-slash"/></button>')
            if (this.value) {
                this.$el.text(new Array(this.value.trim().length).join('●')).data("state", "hide");
                // $span.insertAfter(this.$el);
                this.$el = this.$el.append($span);
                var button = this.$el.find("button.o_show_password_button");
                button.mousedown(function (ev) {
                    self._showSpanPassword(ev);
                })
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
        _showSpanPassword: function (ev) {
            var self = this;
            $(ev.currentTarget).find("span").toggleClass('fa-eye-slash fa-eye');
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
        _setValue: function () {
            var $input = this.$el.find('input');

            return this._super($input.val());
        },
    });

    fieldRegistry.add('wxwork_password', ShowPasswordFieldText);
    return ShowPasswordFieldText;
});
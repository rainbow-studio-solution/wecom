odoo.define('wecom_message.list_copy_button_create', function (require) {
    "use strict";
    var core = require('web.core');
    var _t = core._t;
    var ListView = require('web.ListView');
    var viewRegistry = require('web.view_registry');
    var ListController = require('web.ListController');
    ListController.include({
        renderButtons: function ($node) {
            this._super.apply(this, arguments);
            if (this.$buttons) {
                this.$buttons.on('click', '.o_list_wecom_copy_email_template', this._copy_email_template.bind(this));
                this.$buttons.on('click', '.o_list_wecom_copy_email_template_to_message', this._copy_email_template_to_message.bind(this));
            }
        },
        _copy_email_template: function () {
            // console.log("点击复制")
            var self = this;
            // var records = this.getSelectedIds();
            self._rpc({
                model: 'mail.template',
                method: 'copy_body_html',
                args: [],
            }).then(function (res) {
                if (res) {
                    self.displayNotification({
                        type: 'success',
                        title: _t("Copy successfully!"),
                        message: _t("Copy One-click copy of email template succeeded!"),
                        sticky: false,
                        // className: "bg-success",
                        // next: self.trigger_up('reload')
                        next: {
                            "type": "ir.actions.client",
                            "tag": "reload",
                        }
                    });
                    // self.trigger_up('reload');
                }

            });
        },
        _copy_email_template_to_message: function () {
            var self = this;
            self._rpc({
                model: 'wecom.message.template',
                method: 'copy_mail_template',
                args: [],
            }).then(function (res) {
                if (res) {
                    self.displayNotification({
                        type: 'success',
                        title: _t("Copy successfully!"),
                        message: _t("Copy One-click copy of email template succeeded!"),
                        sticky: false,
                        // className: "bg-success",
                        // next: self.trigger_up('reload')
                        next: {
                            "type": "ir.actions.client",
                            "tag": "reload",
                        }
                    });
                    // self.trigger_up('reload');
                }

            });
        }
    });
});
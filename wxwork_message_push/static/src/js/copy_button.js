odoo.define('wxwork_message_push.list_copy_button_create', function (require) {
    "use strict";
    var ListView = require('web.ListView');
    var viewRegistry = require('web.view_registry');
    var ListController = require('web.ListController');
    ListController.include({
        renderButtons: function ($node) {
            this._super.apply(this, arguments);
            if (this.$buttons) {
                this.$buttons.on('click', '.o_list_wxwork_copy_email_template', this._copy_email_template.bind(this));
            }
        },
        _copy_email_template: function () {
            // console.log("点击复制")
            var self = this;
            // var records = this.getSelectedIds();
            self._rpc({
                    model: 'wxwork.message.template',
                    method: 'copy_mail_template',
                    // args: [records]
                },
                []
            );
        }
    });
});
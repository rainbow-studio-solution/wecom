odoo.define("web.AdvancedDialog", function (require) {
    'use strict';

    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var AbstractWebClient = require('web.AbstractWebClient');

    function AdvancedDialog(parent, action) {
        var dialog = new Dialog(this, action.params);

        dialog.opened().then(function () {
            //打开弹窗后，判断是否刷新页面
            if (action.params["reload"] === 'true') {
                var header_button = dialog.$modal.find("header").find("button");
                var footer_button = dialog.$modal.find("footer").find("button");
                header_button.click(function () {
                    parent.do_action({
                        type: 'ir.actions.client',
                        res_model: 'res.users',
                        tag: 'reload_context',
                        target: 'current',
                    });
                });
                footer_button.click(function () {
                    parent.do_action({
                        type: 'ir.actions.client',
                        res_model: 'res.users',
                        tag: 'reload_context',
                        target: 'current',
                    });
                });
            } else {

            }
        });
        dialog.open();
    }

    // function reloadButtons() {
    //     return [{
    //         text: _t('Confirm'),
    //         classes: 'btn-primary',
    //         close: false,
    //         click: function () {
    //             this.do_action({
    //                 type: 'ir.actions.client',
    //                 res_model: 'res.users',
    //                 tag: 'reload_context',
    //                 target: 'current',
    //             });
    //         }
    //     }];

    // }
    // var AdvancedDialog = Dialog.extend({
    //     init: function (parent, action) {
    //         this._super(parent);
    //     },
    //     start: function (action) {
    //         var self = this;
    //         var dialog = new Dialog(this, action.params);
    //         dialog.opened().then(function () {
    //             //打开弹窗后，判断是否刷新页面
    //             if (action.params["reload"] === 'true') {
    //                 var header_button = dialog.$modal.find("header").find("button");
    //                 var footer_button = dialog.$modal.find("footer").find("button");
    //                 header_button.click(function () {
    //                     self.reloadPage()
    //                 });
    //                 footer_button.click(function () {
    //                     self.reloadPage()
    //                 });
    //             } else {

    //             }
    //         });
    //         dialog.open();
    //     },
    //     reloadPage: function () {
    //         this.do_action({
    //             type: 'ir.actions.client',
    //             res_model: 'res.users',
    //             tag: 'reload_context',
    //             target: 'current',
    //         });
    //     }
    // });
    core.action_registry.add("dialog", AdvancedDialog);

});
odoo.define('wecom_contacts.wecom_organizational_download', function (require) {
    "use strict";
    var core = require('web.core');
    var _t = core._t;

    var ListController = require('web.ListController');
    ListController.include({
        renderButtons: function ($node) {
            this._super.apply(this, arguments);
            if (this.$buttons) {
                this.$buttons.on('click', '.o_list_wecom_organizational_download', this.wecom_organizational_download.bind(this));
            }
        },
        
        wecom_organizational_download: function () {
            var self = this;
            self._rpc({
                model: 'wecom.users',
                method: 'organizational_download',
                args: [],
            }).then(function (res) {
                // console.log(res)
                if (res) {
                    self.displayNotification({
                        type: 'success',
                        title: _t("Downloaded successfully!"),
                        message: _t("Organization structure downloaded successfull!"),
                        sticky: true,
                        buttons: [{
                            text: _t("Refresh"),
                            click: () => {
                                window.location.reload(true);
                            },
                            primary: true
                        }],

                    });
                }
            })
        }
    });
});
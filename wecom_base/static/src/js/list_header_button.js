odoo.define('wecom_api.pull_error_code', function (require) {
    "use strict";
    var core = require('web.core');
    var session = require('web.session');
    var _t = core._t;

    var ListController = require('web.ListController');
    ListController.include({
        renderButtons: function ($node) {
            this._super.apply(this, arguments);
            if (this.$buttons) {
                this.$buttons.on('click', '.o_list_wecom_pull_error_code', this._pull_error_code.bind(this));
            }
        },
        _pull_error_code: function () {
            var self = this;
            self._rpc({
                model: 'wecom.service_api_error',
                method: 'pull',
                args: [],
            }).then(function (res) {
                if (res["state"]) {
                    self.displayNotification({
                        type: 'success',
                        title: _t("Pull successfully!"),
                        // message: _t("Global error code pulled successfully!"),
                        message: res["msg"],
                        sticky: true,
                        buttons: [{
                            text: _t("Refresh"),
                            click: () => {
                                window.location.reload(true);
                            },
                            primary: true
                        }],

                    });
                } else {
                    self.displayNotification({
                        type: 'danger',
                        title: _t("Pull failed!"),
                        message: res["msg"],
                        sticky: true,
                    });
                }
            })
        },

    });
});